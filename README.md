# DebateAI - AI Debate Club Platform

A production-grade AI-powered debate platform where multiple AI agents engage in structured, real-time debates on any topic.

## 🏗️ Architecture

### Monorepo Structure
```
debateai/
├── apps/
│   ├── frontend/          # Next.js 15 + TypeScript + TailwindCSS
│   └── backend/           # FastAPI + Python
├── packages/
│   ├── shared/           # Shared types and utilities
│   └── ui/               # Reusable UI components
├── docker-compose.yml
└── README.md
```

### Tech Stack

**Frontend:**
- Next.js 15 with App Router
- TypeScript
- TailwindCSS + shadcn/ui
- Framer Motion for animations
- Clerk for authentication

**Backend:**
- FastAPI (Python)
- PostgreSQL with Prisma ORM
- WebSockets for real-time communication
- LangGraph for agent orchestration
- OpenAI/Gemini APIs

**AI Agents:**
- Argument Generator Agent
- Counter-Argument Agent
- Fact Checker Agent
- Moderator Agent
- Judge Agent

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd debateai
```

2. Install dependencies
```bash
# Install frontend dependencies
pnpm install

# Install backend dependencies
cd apps/backend
pip install -r requirements.txt
```

3. Set up environment variables
```bash
# Frontend .env.local
cp apps/frontend/.env.example apps/frontend/.env.local

# Backend .env
cp apps/backend/.env.example apps/backend/.env
```

4. Set up database
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Run migrations
cd apps/backend
prisma migrate dev
```

5. Start development servers
```bash
# Start all services
pnpm dev
```

## 🎯 Features

### Core Functionality
- **Real-time AI Debates**: Watch multiple AI agents debate in real-time
- **Structured Debate Flow**: Professional debate format with moderator control
- **Live Fact-Checking**: Real-time claim verification with source citations
- **Multiple Debate Styles**: Formal, aggressive, academic, friendly tones
- **Customizable AI Personalities**: Choose different agent personas

### User Experience
- **ChatGPT-like Interface**: Modern, intuitive UI
- **Debate Timeline**: Visual representation of debate progression
- **Agent Cards**: Animated cards showing agent personalities and avatars
- **Live Fact-Check Badges**: Real-time verification status
- **Session Memory**: Persistent debate history
- **Export Functionality**: Save debates as PDF

### Advanced Features
- **Multi-user Debate Rooms**: Collaborative debate sessions
- **Voice Debate Mode**: Audio-based debates
- **AI-Generated Topics**: Automatic topic suggestions
- **Public Leaderboard**: Debate scoring and rankings
- **Team Debates**: Multiple agents per team
- **AI vs Human Mode**: Join debates yourself

## 🤖 AI Agents

### 1. Argument Generator Agent
- Generates opening arguments
- Researches supporting evidence
- Adapts tone based on debate style

### 2. Counter-Argument Agent
- Identifies logical fallacies
- Provides rebuttals with evidence
- Challenges opponent claims

### 3. Fact Checker Agent
- Real-time claim verification
- Source citation and credibility scoring
- Flags misleading or unsupported claims

### 4. Moderator Agent
- Controls debate flow
- Enforces debate rules
- Provides round summaries

### 5. Judge Agent
- Evaluates argument quality
- Scores debate performance
- Provides final verdict with reasoning

## 🎨 UI Design

Inspired by modern AI platforms:
- **Perplexity**: Clean, information-rich interface
- **ChatGPT**: Conversational UI patterns
- **Linear**: Minimalist design language
- **Vercel**: Developer-focused aesthetics

### Pages
1. **Landing Page**: Hero, features, pricing, testimonials
2. **Dashboard**: Debate history, analytics, settings
3. **Live Debate Room**: Real-time debate interface
4. **Debate History**: Browse past debates
5. **Agent Configuration**: Customize AI personalities
6. **Analytics**: Usage statistics and insights

## 🔧 Development

### Frontend Development
```bash
cd apps/frontend
pnpm dev
```

### Backend Development
```bash
cd apps/backend
uvicorn main:app --reload
```

### Database Operations
```bash
cd apps/backend
prisma studio          # Open database GUI
prisma migrate dev      # Run migrations
prisma generate        # Generate Prisma client
```

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📊 API Documentation

Backend API documentation available at:
- Development: http://localhost:8000/docs
- Production: https://api.debateai.com/docs

## 🔐 Authentication

Uses Clerk for secure authentication:
- Social login options
- Session management
- User profile management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Documentation: [docs.debateai.com](https://docs.debateai.com)
- Issues: [GitHub Issues](https://github.com/your-org/debateai/issues)
- Discord: [Community Server](https://discord.gg/debateai)
