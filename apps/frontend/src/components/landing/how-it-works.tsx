"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, MessageSquare, Users, Zap, Shield } from 'lucide-react'

const steps = [
  {
    number: 1,
    title: "Enter Topic",
    description: "Start by entering any debate topic you're interested in.",
    icon: Brain,
    color: "from-blue-500 to-purple-600"
  },
  {
    number: 2,
    title: "Configure Debate",
    description: "Choose debate style, number of rounds, AI personalities, and tone.",
    icon: MessageSquare,
    color: "from-green-500 to-emerald-600"
  },
  {
    number: 3,
    title: "AI Agents Join",
    description: "Multiple AI agents with different roles join the debate room.",
    icon: Users,
    color: "from-orange-500 to-red-600"
  },
  {
    number: 4,
    title: "Live Debate",
    description: "Watch agents argue, rebut, and fact-check in real-time.",
    icon: Zap,
    color: "from-purple-500 to-pink-600"
  },
  {
    number: 5,
    title: "Verdict & Analysis",
    description: "Judge agent provides final verdict with detailed scoring.",
    icon: Shield,
    color: "from-yellow-500 to-orange-600"
  }
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
              How It Works
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Get started with DebateAI in just a few simple steps
            </p>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="relative"
            >
              {/* Connection Line */}
              {index < steps.length - 1 && (
                <motion.div
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
                  className="absolute top-8 left-1/2 w-full h-0.5 bg-gradient-to-r from-blue-500 to-purple-600 origin-left"
                  style={{
                    clipPath: `polygon(0 50%, 100% 50%, 100% 50%)`
                  }}
                />
              )}

              <Card className="h-full relative overflow-hidden">
                <CardHeader className="pb-4">
                  <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${step.color}`}>
                    <step.icon className="h-8 w-8 text-white" />
                  </div>
                  <CardTitle className="mt-4 text-xl font-semibold">
                    Step {step.number}
                  </CardTitle>
                  <Badge variant="secondary" className="ml-2">
                    {step.title}
                  </Badge>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                </CardContent>
              </Card>

              {/* Step Number Badge */}
              <div className={`absolute -top-2 -right-2 w-8 h-8 rounded-full bg-gradient-to-r ${step.color} flex items-center justify-center text-white font-bold text-sm shadow-lg`}>
                {step.number}
              </div>
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-16 text-center"
        >
          <h3 className="text-2xl font-semibold mb-4">
            Ready to Start Your First Debate?
          </h3>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of users already experiencing the future of AI-powered debates
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 rounded-lg font-semibold transition-colors">
              Start Your First Debate
            </button>
            <button className="border border-border bg-background hover:bg-accent hover:text-accent-foreground px-8 py-3 rounded-lg font-semibold transition-colors">
              Watch Live Demo
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
