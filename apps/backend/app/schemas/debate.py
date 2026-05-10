from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DebateStyle(str, Enum):
    FORMAL = "formal"
    AGGRESSIVE = "aggressive"
    ACADEMIC = "academic"
    FRIENDLY = "friendly"

class DebateStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AgentRole(str, Enum):
    MODERATOR = "moderator"
    PRO_ARGUMENT = "pro_argument"
    CON_ARGUMENT = "con_argument"
    FACT_CHECKER = "fact_checker"
    JUDGE = "judge"

class FactCheckStatus(str, Enum):
    VERIFIED = "verified"
    MISLEADING = "misleading"
    UNSUPPORTED = "unsupported"
    PENDING = "pending"

# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseSchema):
    email: str
    name: str
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    clerk_id: str

class User(UserBase):
    id: int
    clerk_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# Agent schemas
class AgentBase(BaseSchema):
    name: str
    role: AgentRole
    personality: Optional[str] = None
    system_prompt: str
    avatar_url: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Debate schemas
class DebateCreate(BaseSchema):
    topic: str = Field(..., min_length=1, max_length=500)
    style: DebateStyle
    rounds: int = Field(default=3, ge=1, le=10)
    tone: str = Field(default="formal")
    agent_personalities: Optional[Dict[str, Any]] = None

class DebateUpdate(BaseSchema):
    topic: Optional[str] = Field(None, min_length=1, max_length=500)
    style: Optional[DebateStyle] = None
    rounds: Optional[int] = Field(None, ge=1, le=10)
    tone: Optional[str] = None
    status: Optional[DebateStatus] = None
    agent_personalities: Optional[Dict[str, Any]] = None

class Debate(BaseSchema):
    id: int
    user_id: int
    topic: str
    style: DebateStyle
    status: DebateStatus
    rounds: int
    tone: str
    agent_personalities: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[User] = None

# Message schemas
class MessageCreate(BaseSchema):
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = Field(default="argument")
    agent_id: int

class Message(BaseSchema):
    id: int
    debate_id: int
    round_id: int
    agent_id: int
    content: str
    message_type: str
    token_count: int
    created_at: datetime
    agent: Optional[Agent] = None

# Debate Round schemas
class DebateRoundCreate(BaseSchema):
    round_number: int
    debate_id: int

class DebateRound(BaseSchema):
    id: int
    debate_id: int
    round_number: int
    status: str
    summary: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: Optional[List[Message]] = None

# Fact Check schemas
class FactCheckCreate(BaseSchema):
    claim: str = Field(..., min_length=1, max_length=1000)
    message_id: int

class FactCheck(BaseSchema):
    id: int
    debate_id: int
    message_id: int
    claim: str
    status: FactCheckStatus
    confidence_score: int
    sources: Optional[List[str]] = None
    reasoning: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Analytics schemas
class AnalyticsCreate(BaseSchema):
    user_id: int
    debate_id: int
    total_tokens: int = 0
    total_cost: float = 0.0
    duration_seconds: int = 0
    participant_count: int = 0
    fact_check_count: int = 0

class Analytics(BaseSchema):
    id: int
    user_id: int
    debate_id: int
    total_tokens: int
    total_cost: float
    duration_seconds: int
    participant_count: int
    fact_check_count: int
    created_at: datetime

# WebSocket message schemas
class WebSocketMessage(BaseSchema):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DebateStateUpdate(BaseSchema):
    debate_id: int
    status: DebateStatus
    current_round: Optional[int] = None
    current_agent: Optional[str] = None
    message: Optional[str] = None

class AgentMessage(BaseSchema):
    agent_id: int
    agent_name: str
    agent_role: AgentRole
    content: str
    message_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    token_count: Optional[int] = None

class FactCheckUpdate(BaseSchema):
    message_id: int
    claim: str
    status: FactCheckStatus
    confidence_score: int
    sources: Optional[List[str]] = None
    reasoning: Optional[str] = None

# Response schemas
class DebateResponse(BaseSchema):
    success: bool
    message: str
    data: Optional[Debate] = None

class DebatesListResponse(BaseSchema):
    success: bool
    message: str
    data: List[Debate]
    total: int
    page: int
    per_page: int

class MessageResponse(BaseSchema):
    success: bool
    message: str
    data: Optional[Message] = None

class MessagesListResponse(BaseSchema):
    success: bool
    message: str
    data: List[Message]
    total: int
    page: int
    per_page: int
