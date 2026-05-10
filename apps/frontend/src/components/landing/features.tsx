"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, MessageSquare, Users, Zap, Shield, TrendingUp } from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: "AI-Powered Debates",
    description: "Watch multiple AI agents with different personalities engage in structured debates on any topic.",
    color: "from-blue-500 to-purple-600"
  },
  {
    icon: MessageSquare,
    title: "Real-Time Streaming",
    description: "Experience debates as they happen with live streaming responses and instant fact-checking.",
    color: "from-green-500 to-emerald-600"
  },
  {
    icon: Users,
    title: "Multiple Debate Styles",
    description: "Choose from formal, aggressive, academic, or friendly debate formats.",
    color: "from-orange-500 to-red-600"
  },
  {
    icon: Shield,
    title: "Live Fact-Checking",
    description: "Claims are verified in real-time using external APIs with confidence scores.",
    color: "from-purple-500 to-pink-600"
  },
  {
    icon: Zap,
    title: "Instant Analytics",
    description: "Get detailed insights into debate performance, token usage, and argument quality.",
    color: "from-yellow-500 to-orange-600"
  },
  {
    icon: TrendingUp,
    title: "Export & Share",
    description: "Export debates as PDF, share with others, and build your debate history.",
    color: "from-indigo-500 to-blue-600"
  }
]

export function Features() {
  return (
    <section id="features" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight gradient-text">
              Powerful Features
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need for intelligent, engaging debates powered by cutting-edge AI technology.
            </p>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
            >
              <Card className="h-full group cursor-pointer transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
                <CardHeader className="pb-4">
                  <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${feature.color}`}>
                    <feature.icon className="h-8 w-8 text-white" />
                  </div>
                  <CardTitle className="mt-4 text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Additional Features Grid */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-8">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-6 w-6 text-primary" />
                  <span>Advanced AI Agents</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-start space-x-3">
                    <Badge variant="secondary" className="mt-1">Pro Argument</Badge>
                    <span className="text-sm">Evidence-driven, persuasive arguments supporting the topic</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <Badge variant="secondary" className="mt-1">Con Argument</Badge>
                    <span className="text-sm">Critical analysis and counter-arguments against the topic</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <Badge variant="secondary" className="mt-1">Fact Checker</Badge>
                    <span className="text-sm">Real-time claim verification with source citations</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <Badge variant="secondary" className="mt-1">Moderator</Badge>
                    <span className="text-sm">Maintains order and ensures fair debate flow</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <Badge variant="secondary" className="mt-1">Judge</Badge>
                    <span className="text-sm">Provides final verdict with detailed scoring</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-6 w-6 text-primary" />
                  <span>Smart Analytics</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span className="text-sm">Token usage tracking</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full" />
                    <span className="text-sm">Argument quality scoring</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-purple-500 rounded-full" />
                    <span className="text-sm">Fact-check accuracy metrics</span>
                  </li>
                  <li className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-orange-500 rounded-full" />
                    <span className="text-sm">Debate performance insights</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
