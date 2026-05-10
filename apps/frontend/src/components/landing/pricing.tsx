"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Check, Zap, Crown, Sparkles } from 'lucide-react'

const plans = [
  {
    name: "Free",
    price: "$0",
    description: "Perfect for trying out DebateAI",
    icon: Sparkles,
    features: [
      "3 debates per month",
      "Basic AI agents",
      "Standard debate styles",
      "Community support",
      "Basic analytics"
    ],
    highlighted: false,
    buttonText: "Get Started"
  },
  {
    name: "Pro",
    price: "$29",
    description: "For serious debaters and researchers",
    icon: Zap,
    features: [
      "Unlimited debates",
      "Advanced AI agents",
      "All debate styles",
      "Priority support",
      "Advanced analytics",
      "Export to PDF",
      "Custom AI personalities",
      "Team collaboration"
    ],
    highlighted: true,
    buttonText: "Start Free Trial"
  },
  {
    name: "Enterprise",
    price: "Custom",
    description: "For teams and organizations",
    icon: Crown,
    features: [
      "Everything in Pro",
      "Custom integrations",
      "Dedicated support",
      "White-label options",
      "Advanced security",
      "SLA guarantee",
      "Training sessions",
      "API access"
    ],
    highlighted: false,
    buttonText: "Contact Sales"
  }
]

export function Pricing() {
  return (
    <section id="pricing" className="py-20 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight">
              Choose Your Plan
            </h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Start free and scale as your debating needs grow
            </p>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="relative"
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                    MOST POPULAR
                  </Badge>
                </div>
              )}

              <Card className={`h-full relative overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${
                plan.highlighted 
                  ? 'ring-2 ring-primary ring-offset-4 bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200' 
                  : 'border-border'
              }`}>
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`inline-flex p-3 rounded-lg ${
                      plan.highlighted 
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600' 
                        : 'bg-muted'
                    }`}>
                      <plan.icon className={`h-8 w-8 ${
                        plan.highlighted ? 'text-white' : 'text-muted-foreground'
                      }`} />
                    </div>
                    {plan.name === "Pro" && (
                      <Badge variant="secondary" className="animate-pulse">
                        14-day trial
                      </Badge>
                    )}
                  </div>
                  
                  <CardTitle className="text-2xl font-bold mb-2">
                    {plan.name}
                  </CardTitle>
                  
                  <div className="flex items-baseline">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    {plan.price !== "Custom" && (
                      <span className="text-muted-foreground ml-1">/month</span>
                    )}
                  </div>
                  
                  <p className="text-sm text-muted-foreground mt-2">
                    {plan.description}
                  </p>
                </CardHeader>
                
                <CardContent className="pt-0">
                  <ul className="space-y-3">
                    {plan.features.map((feature, featureIndex) => (
                      <motion.li
                        key={feature}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: featureIndex * 0.1 }}
                        className="flex items-center space-x-3"
                      >
                        <Check className="h-5 w-5 text-green-600 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </motion.li>
                    ))}
                  </ul>
                  
                  <div className="mt-8">
                    <Button 
                      className={`w-full ${
                        plan.highlighted 
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700' 
                          : ''
                      }`}
                      size="lg"
                    >
                      {plan.buttonText}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-16"
        >
          <Card className="bg-background">
            <CardHeader>
              <CardTitle className="text-center">Frequently Asked Questions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-2">Can I change plans anytime?</h4>
                    <p className="text-sm text-muted-foreground">
                      Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">What AI models are included?</h4>
                    <p className="text-sm text-muted-foreground">
                      We use GPT-4, Claude, and Gemini models depending on the task and your plan.
                    </p>
                  </div>
                </div>
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-2">Is there a free trial?</h4>
                    <p className="text-sm text-muted-foreground">
                      Yes! Pro plan comes with a 14-day free trial. No credit card required.
                    </p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Can I export debates?</h4>
                    <p className="text-sm text-muted-foreground">
                      Pro and Enterprise plans include PDF export. Free plan users can view debates online.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
