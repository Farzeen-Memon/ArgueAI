from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from .core.database import Base

class DebateStyle(PyEnum):
    FORMAL = "formal"
    AGGRESSIVE = "aggressive"
    ACADEMIC = "academic"
    FRIENDLY = "friendly"

class DebateStatus(PyEnum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AgentRole(PyEnum):
    MODERATOR = "moderator"
    PRO_ARGUMENT = "pro_argument"
    CON_ARGUMENT = "con_argument"
    FACT_CHECKER = "fact_checker"
    JUDGE = "judge"

class FactCheckStatus(PyEnum):
    VERIFIED = "verified"
    MISLEADING = "misleading"
    UNSUPPORTED = "unsupported"
    PENDING = "pending"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    debates = relationship("Debate", back_populates="user")

class Debate(Base):
    __tablename__ = "debates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    style = Column(Enum(DebateStyle), nullable=False)
    status = Column(Enum(DebateStatus), default=DebateStatus.PENDING)
    rounds = Column(Integer, default=3)
    tone = Column(String, default="formal")
    agent_personalities = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="debates")
    debate_rounds = relationship("DebateRound", back_populates="debate")
    messages = relationship("Message", back_populates="debate")
    fact_checks = relationship("FactCheck", back_populates="debate")

class DebateRound(Base):
    __tablename__ = "debate_rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    status = Column(String, default="active")
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    debate = relationship("Debate", back_populates="debate_rounds")
    messages = relationship("Message", back_populates="round")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(Enum(AgentRole), nullable=False)
    personality = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="agent")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"), nullable=False)
    round_id = Column(Integer, ForeignKey("debate_rounds.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String, default="argument")  # argument, rebuttal, moderation, fact_check, verdict
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    debate = relationship("Debate", back_populates="messages")
    round = relationship("DebateRound", back_populates="messages")
    agent = relationship("Agent", back_populates="messages")
    fact_checks = relationship("FactCheck", back_populates="message")

class FactCheck(Base):
    __tablename__ = "fact_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    claim = Column(Text, nullable=False)
    status = Column(Enum(FactCheckStatus), default=FactCheckStatus.PENDING)
    confidence_score = Column(Integer, default=0)  # 0-100
    sources = Column(JSON, nullable=True)  # List of source URLs
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    debate = relationship("Debate", back_populates="fact_checks")
    message = relationship("Message", back_populates="fact_checks")

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    debate_id = Column(Integer, ForeignKey("debates.id"), nullable=False)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    duration_seconds = Column(Integer, default=0)
    participant_count = Column(Integer, default=0)
    fact_check_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    debate = relationship("Debate")
