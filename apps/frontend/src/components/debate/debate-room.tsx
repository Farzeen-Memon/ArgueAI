"use client"

import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { AgentCard } from './agent-card'
import { MessageBubble } from './message-bubble'
import { DebateTimeline } from './debate-timeline'
import { cn } from '@/lib/utils'

interface DebateRoomProps {
  debateId: string
  userId: string
}

interface Message {
  id: string
  agent_id: number
  agent_name: string
  agent_role: string
  content: string
  message_type: string
  created_at: string
  token_count: number
}

interface Agent {
  id: number
  name: string
  role: string
  personality: string
  avatar_url?: string
  is_active?: boolean
  is_typing?: boolean
}

export function DebateRoom({ debateId, userId }: DebateRoomProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [currentRound, setCurrentRound] = useState(1)
  const [totalRounds, setTotalRounds] = useState(3)
  const [debateStatus, setDebateStatus] = useState<'pending' | 'active' | 'completed'>('pending')
  const [isConnected, setIsConnected] = useState(false)
  const [topic, setTopic] = useState('')
  const [style, setStyle] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Initialize WebSocket connection
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws/debate/${debateId}`
    wsRef.current = new WebSocket(wsUrl)

    wsRef.current.onopen = () => {
      setIsConnected(true)
      // Join debate room
      wsRef.current?.send(JSON.stringify({
        type: 'join_debate',
        user_id: userId
      }))
    }

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }

    wsRef.current.onclose = () => {
      setIsConnected(false)
    }

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsConnected(false)
    }

    return () => {
      wsRef.current?.close()
    }
  }, [debateId, userId])

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'debate_state':
        setTopic(data.data.topic)
        setStyle(data.data.style)
        setTotalRounds(data.data.rounds)
        setDebateStatus(data.data.status)
        break

      case 'new_message':
        setMessages(prev => [...prev, data.data])
        break

      case 'agent_typing':
        setAgents(prev => prev.map(agent => 
          agent.id === data.data.agent_id 
            ? { ...agent, is_typing: data.data.is_typing }
            : agent
        ))
        break

      case 'debate_started':
        setDebateStatus('active')
        break

      case 'debate_stopped':
        setDebateStatus('completed')
        break

      case 'fact_check_result':
        // Handle fact check results
        setMessages(prev => [...prev, {
          id: `fact-check-${data.data.message_id}`,
          agent_id: 0,
          agent_name: 'Fact Checker',
          agent_role: 'fact_checker',
          content: formatFactCheckResult(data.data),
          message_type: 'fact_check',
          created_at: new Date().toISOString(),
          token_count: 0
        }])
        break
    }
  }

  const formatFactCheckResult = (data: any) => {
    const statusEmoji = {
      verified: '✅',
      misleading: '⚠️',
      unsupported: '❓'
    }

    return `**Fact Check Result:**\n\n${statusEmoji[data.status as keyof typeof statusEmoji]} **Claim:** ${data.claim}\n\n**Status:** ${data.status}\n**Confidence:** ${data.confidence_score}/100\n\n**Reasoning:** ${data.reasoning}`
  }

  const startDebate = () => {
    wsRef.current?.send(JSON.stringify({
      type: 'start_debate',
      user_id: userId
    }))
  }

  const stopDebate = () => {
    wsRef.current?.send(JSON.stringify({
      type: 'stop_debate',
      user_id: userId
    }))
  }

  const requestFactCheck = (messageId: string, claim: string) => {
    wsRef.current?.send(JSON.stringify({
      type: 'fact_check',
      user_id: userId,
      message_id: messageId,
      claim: claim
    }))
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar - Agent Cards */}
      <div className="w-80 border-r bg-muted/30 p-4 overflow-y-auto">
        <div className="space-y-4">
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Debate Participants</h2>
            <div className="flex items-center space-x-2 mb-4">
              <Badge variant={isConnected ? "default" : "destructive"}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </Badge>
              <Badge variant="outline">
                Round {currentRound}/{totalRounds}
              </Badge>
            </div>
          </div>

          {/* Agent Cards */}
          <div className="space-y-3">
            {agents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                className="cursor-pointer hover:shadow-md transition-shadow"
              />
            ))}
          </div>

          {/* Debate Controls */}
          <div className="pt-4 border-t">
            <h3 className="text-sm font-medium mb-3">Controls</h3>
            <div className="space-y-2">
              {debateStatus === 'pending' && (
                <Button onClick={startDebate} className="w-full">
                  Start Debate
                </Button>
              )}
              {debateStatus === 'active' && (
                <Button onClick={stopDebate} variant="outline" className="w-full">
                  Stop Debate
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold">{topic}</h1>
              <p className="text-sm text-muted-foreground">
                {style} • {debateStatus} • Round {currentRound}/{totalRounds}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant={debateStatus === 'active' ? 'default' : 'secondary'}>
                {debateStatus}
              </Badge>
            </div>
          </div>
        </div>

        {/* Debate Content */}
        <div className="flex-1 flex">
          {/* Messages Area */}
          <div className="flex-1 flex flex-col">
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4">
                <AnimatePresence>
                  {messages.map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <MessageBubble
                        message={message}
                        onFactCheck={requestFactCheck}
                        isLast={index === messages.length - 1}
                      />
                    </motion.div>
                  ))}
                </AnimatePresence>
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
          </div>

          {/* Timeline Sidebar */}
          <div className="w-80 border-l bg-muted/20 p-4">
            <DebateTimeline
              messages={messages}
              currentRound={currentRound}
              totalRounds={totalRounds}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
