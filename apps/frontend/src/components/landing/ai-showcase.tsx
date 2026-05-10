"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, MessageSquare, Users, Shield, Zap } from 'lucide-react'

const agents = [
  {
    name: "Pro Argument Agent",
    role: "pro_argument",
    description: "Specializes in constructing persuasive arguments with strong evidence support",
    icon: MessageSquare,
    color: "from-green-500 to-emerald-600",
    capabilities: ["Evidence Research", "Logical Reasoning", "Persuasive Writing"]
  },
  {
    name: "Con Argument Agent", 
    role: "con_argument",
    description: "Expert at identifying logical fallacies and providing critical counter-arguments",
    icon: Brain,
    color: "from-red-500 to-rose-600",
    capabilities: ["Critical Analysis", "Logical Fallacy Detection", "Counter-Argumentation"]
  },
  {
    name: "Fact Checker Agent",
    role: "fact_checker", 
    description: "Verifies claims in real-time using multiple data sources and APIs",
    icon: Shield,
    color: "from-purple-500 to-pink-600",
    capabilities: ["Real-time Verification", "Source Citation", "Confidence Scoring"]
  },
  {
    name: "Moderator Agent",
    role: "moderator",
    description: "Ensures fair debate flow and maintains professional discourse standards",
    icon: Users,
    color: "from-blue-500 to-indigo-600", 
    capabilities: ["Flow Control", "Rule Enforcement", "Time Management"]
  },
  {
    name: "Judge Agent",
    role: "judge",
    description: "Evaluates argument quality and provides final verdict with detailed scoring",
    icon: Zap,
    color: "from-yellow-500 to-orange-600",
    capabilities: ["Quality Assessment", "Performance Scoring", "Final Verdict"]
  }
]

export function AIShowcase() {
  return (
    <section id="ai-showcase" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight gradient-text">
              Meet Our AI Agents
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Each agent is specialized with unique personalities and capabilities for engaging debates
            </p>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {agents.map((agent, index) => (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -10 }}
            >
              <Card className="h-full group cursor-pointer transition-all duration-300 hover:shadow-xl hover:-translate-y-2">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${agent.color}`}>
                      <agent.icon className="h-8 w-8 text-white" />
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {agent.role.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>
                  <CardTitle className="text-xl font-semibold">{agent.name}</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-muted-foreground leading-relaxed mb-4">
                    {agent.description}
                  </p>
                  
                  <div>
                    <h4 className="text-sm font-semibold mb-2 text-primary">Capabilities:</h4>
                    <div className="flex flex-wrap gap-2">
                      {agent.capabilities.map((capability) => (
                        <Badge key={capability} variant="outline" className="text-xs">
                          {capability}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">
                        Powered by advanced LLMs
                      </span>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-75" />
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-150" />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Agent Interaction Preview */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-16"
        >
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-center">Agent Collaboration</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <div className="grid grid-cols-5 gap-4 mb-6">
                {agents.map((agent) => (
                  <div key={agent.name} className="text-center">
                    <div className={`w-12 h-12 mx-auto rounded-full bg-gradient-to-r ${agent.color} flex items-center justify-center mb-2`}>
                      <agent.icon className="h-6 w-6 text-white" />
                    </div>
                    <p className="text-xs font-medium">{agent.name.split(' ')[0]}</p>
                  </div>
                ))}
              </div>
              
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-4">
                  Watch our agents work together in perfect harmony
                </p>
                <motion.div
                  animate={{ x: [0, 10, 0, -10, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="inline-flex items-center space-x-1"
                >
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                  <div className="w-2 h-2 bg-purple-500 rounded-full" />
                  <div className="w-2 h-2 bg-red-500 rounded-full" />
                  <div className="w-2 h-2 bg-yellow-500 rounded-full" />
                </motion.div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
