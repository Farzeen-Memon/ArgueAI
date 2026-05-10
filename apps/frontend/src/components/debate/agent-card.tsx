"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface AgentCardProps {
  agent: {
    id: number
    name: string
    role: string
    personality: string
    avatar_url?: string
    is_active?: boolean
    is_typing?: boolean
  }
  className?: string
}

const roleColors = {
  moderator: 'bg-blue-500',
  pro_argument: 'bg-green-500',
  con_argument: 'bg-red-500',
  fact_checker: 'bg-purple-500',
  judge: 'bg-yellow-500'
}

const roleEmojis = {
  moderator: '⚖️',
  pro_argument: '✅',
  con_argument: '❌',
  fact_checker: '🔍',
  judge: '🏛️'
}

export function AgentCard({ agent, className }: AgentCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
      className={cn("w-full", className)}
    >
      <Card className={cn(
        "relative overflow-hidden transition-all duration-300",
        agent.is_active && "ring-2 ring-primary ring-offset-2",
        agent.is_typing && "animate-pulse"
      )}>
        <CardContent className="p-4">
          <div className="flex items-start space-x-3">
            {/* Avatar */}
            <div className="relative">
              <Avatar className="h-12 w-12">
                <AvatarImage src={agent.avatar_url} alt={agent.name} />
                <AvatarFallback className={cn(roleColors[agent.role as keyof typeof roleColors])}>
                  {roleEmojis[agent.role as keyof typeof roleEmojis]}
                </AvatarFallback>
              </Avatar>
              
              {/* Active indicator */}
              {agent.is_active && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -bottom-1 -right-1 h-4 w-4 bg-green-500 rounded-full border-2 border-background"
                />
              )}
              
              {/* Typing indicator */}
              {agent.is_typing && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute -bottom-1 -right-1 h-4 w-4 bg-orange-500 rounded-full border-2 border-background"
                />
              )}
            </div>
            
            {/* Agent Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <h3 className="font-semibold text-sm truncate">{agent.name}</h3>
                <Badge variant="secondary" className="text-xs">
                  {agent.role.replace('_', ' ').toUpperCase()}
                </Badge>
              </div>
              
              <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                {agent.personality}
              </p>
              
              {/* Status */}
              <div className="flex items-center space-x-2">
                {agent.is_active && (
                  <span className="text-xs text-green-600 font-medium">Active</span>
                )}
                {agent.is_typing && (
                  <motion.span
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="text-xs text-orange-600 font-medium"
                  >
                    Typing...
                  </motion.span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
