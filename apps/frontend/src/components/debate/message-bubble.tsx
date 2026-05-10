"use client"

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'
import { Copy, CheckCircle } from 'lucide-react'

interface MessageBubbleProps {
  message: {
    id: string
    agent_id: number
    agent_name: string
    agent_role: string
    content: string
    message_type: string
    created_at: string
    token_count: number
  }
  onFactCheck?: (messageId: string, claim: string) => void
  isLast?: boolean
}

const messageColors = {
  moderator: 'bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800',
  pro_argument: 'bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800',
  con_argument: 'bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800',
  fact_checker: 'bg-purple-50 border-purple-200 dark:bg-purple-950 dark:border-purple-800',
  judge: 'bg-yellow-50 border-yellow-200 dark:bg-yellow-950 dark:border-yellow-800'
}

const roleEmojis = {
  moderator: '⚖️',
  pro_argument: '✅',
  con_argument: '❌',
  fact_checker: '🔍',
  judge: '🏛️'
}

export function MessageBubble({ message, onFactCheck, isLast }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false)
  const [isFactChecking, setIsFactChecking] = useState(false)

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const requestFactCheck = () => {
    if (onFactCheck && !isFactChecking) {
      setIsFactChecking(true)
      onFactCheck(message.id, message.content)
      setTimeout(() => setIsFactChecking(false), 3000)
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getMessageIcon = () => {
    switch (message.message_type) {
      case 'moderation':
        return '📢'
      case 'argument':
        return '💬'
      case 'rebuttal':
        return '⚔️'
      case 'fact_check':
        return '🔍'
      case 'verdict':
        return '⚖️'
      default:
        return '💬'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, delay: isLast ? 0 : 0.1 }}
      className={cn("mb-4", isLast && "mb-8")}
    >
      <Card className={cn(
        "overflow-hidden transition-all duration-300 hover:shadow-md",
        messageColors[message.agent_role as keyof typeof messageColors]
      )}>
        <CardContent className="p-4">
          {/* Message Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-3">
              {/* Agent Avatar */}
              <Avatar className="h-8 w-8">
                <AvatarImage src={`/avatars/${message.agent_role}.png`} alt={message.agent_name} />
                <AvatarFallback className="text-xs">
                  {roleEmojis[message.agent_role as keyof typeof roleEmojis]}
                </AvatarFallback>
              </Avatar>
              
              {/* Agent Info */}
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="font-semibold text-sm">{message.agent_name}</h4>
                  <Badge variant="outline" className="text-xs">
                    {message.message_type.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
                <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                  <span>{formatTime(message.created_at)}</span>
                  <span>•</span>
                  <span>{message.token_count} tokens</span>
                </div>
              </div>
            </div>

            {/* Message Actions */}
            <div className="flex items-center space-x-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={copyToClipboard}
                className="h-8 w-8 p-0"
              >
                {copied ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
              
              {message.message_type === 'argument' && onFactCheck && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={requestFactCheck}
                  disabled={isFactChecking}
                  className="h-8 px-2 text-xs"
                >
                  {isFactChecking ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity }}
                      className="h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"
                    />
                  ) : (
                    'Fact Check'
                  )}
                </Button>
              )}
            </div>
          </div>

          {/* Message Content */}
          <div className="relative">
            {/* Message Type Icon */}
            <div className="absolute -top-2 -left-2 text-lg opacity-50">
              {getMessageIcon()}
            </div>
            
            {/* Content */}
            <div className="pl-6 debate-message">
              {message.message_type === 'fact_check' ? (
                <div 
                  className="prose prose-sm max-w-none dark:prose-invert"
                  dangerouslySetInnerHTML={{ __html: message.content }}
                />
              ) : (
                <p className="text-sm leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </p>
              )}
            </div>
          </div>

          {/* Message Footer */}
          {message.agent_role === 'fact_checker' && (
            <div className="mt-3 pt-3 border-t border-dashed">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">
                  Fact check completed
                </span>
                <Badge variant="secondary" className="text-xs">
                  AI VERIFIED
                </Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
