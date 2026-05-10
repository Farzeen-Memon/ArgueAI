"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import { Clock, MessageSquare, CheckCircle } from 'lucide-react'

interface DebateTimelineProps {
  messages: Array<{
    id: string
    agent_role: string
    message_type: string
    created_at: string
  }>
  currentRound: number
  totalRounds: number
}

interface RoundSummary {
  round: number
  messages: number
  hasVerdict: boolean
  progress: number
}

export function DebateTimeline({ messages, currentRound, totalRounds }: DebateTimelineProps) {
  // Group messages by rounds (simplified - in real app, this would come from API)
  const roundSummaries: RoundSummary[] = Array.from({ length: totalRounds }, (_, i) => {
    const roundNumber = i + 1
    const roundMessages = messages.filter(msg => {
      // Simplified round assignment - in real app, this would be more sophisticated
      const msgIndex = messages.indexOf(msg)
      return Math.floor(msgIndex / 6) === i  // Approx 6 messages per round
    })
    
    return {
      round: roundNumber,
      messages: roundMessages.length,
      hasVerdict: roundMessages.some(msg => msg.message_type === 'verdict'),
      progress: roundNumber === currentRound ? 
        (roundMessages.length / 6) * 100 : 
        roundNumber < currentRound ? 100 : 0
    }
  })

  const getRoundStatus = (summary: RoundSummary) => {
    if (summary.round === currentRound) return 'active'
    if (summary.round < currentRound) return 'completed'
    return 'pending'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'active':
        return <Clock className="h-4 w-4 text-blue-600 animate-pulse" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800'
      case 'active':
        return 'bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800'
      default:
        return 'bg-gray-50 border-gray-200 dark:bg-gray-950 dark:border-gray-800'
    }
  }

  return (
    <div className="space-y-4">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center space-x-2">
          <MessageSquare className="h-5 w-5" />
          <span>Debate Timeline</span>
        </CardTitle>
      </CardHeader>

      <div className="space-y-3">
        {roundSummaries.map((summary, index) => {
          const status = getRoundStatus(summary)
          const isActive = status === 'active'
          
          return (
            <motion.div
              key={summary.round}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card className={cn(
                "transition-all duration-300 cursor-pointer hover:shadow-md",
                getStatusColor(status),
                isActive && "ring-2 ring-primary ring-offset-2"
              )}>
                <CardContent className="p-4">
                  {/* Round Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-semibold">Round {summary.round}</h3>
                      {getStatusIcon(status)}
                    </div>
                    <Badge 
                      variant={status === 'active' ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {status}
                    </Badge>
                  </div>

                  {/* Round Progress */}
                  {isActive && (
                    <div className="mb-3">
                      <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                        <span>Progress</span>
                        <span>{Math.round(summary.progress)}%</span>
                      </div>
                      <Progress value={summary.progress} className="h-2" />
                    </div>
                  )}

                  {/* Round Stats */}
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex items-center space-x-2">
                      <MessageSquare className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">Messages:</span>
                      <span className="font-medium">{summary.messages}</span>
                    </div>
                    
                    {summary.hasVerdict && (
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-muted-foreground">Verdict:</span>
                        <span className="font-medium text-green-600">Ready</span>
                      </div>
                    )}
                  </div>

                  {/* Round Preview */}
                  {status !== 'pending' && summary.messages > 0 && (
                    <div className="mt-3 pt-3 border-t">
                      <div className="text-xs text-muted-foreground mb-1">
                        Recent Activity
                      </div>
                      <div className="space-y-1">
                        {messages
                          .filter(msg => Math.floor(messages.indexOf(msg) / 6) === index)
                          .slice(-2)
                          .map(msg => (
                            <div key={msg.id} className="flex items-center space-x-2 text-xs">
                              <Badge variant="outline" className="text-xs px-1 py-0">
                                {msg.agent_role.replace('_', ' ').slice(0, 3).toUpperCase()}
                              </Badge>
                              <span className="truncate">
                                {msg.message_type.replace('_', ' ')}
                              </span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}

                  {/* Current Round Indicator */}
                  {isActive && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="mt-3 pt-3 border-t"
                    >
                      <div className="flex items-center space-x-2 text-xs text-blue-600">
                        <motion.div
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                          className="h-2 w-2 bg-blue-600 rounded-full"
                        />
                        <span>Round in progress</span>
                      </div>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )
        })}

        {/* Debate Completion Indicator */}
        {currentRound > totalRounds && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800">
              <CardContent className="p-4 text-center">
                <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <h3 className="font-semibold text-green-600 mb-1">
                  Debate Completed
                </h3>
                <p className="text-sm text-muted-foreground">
                  All {totalRounds} rounds have been completed
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  )
}
