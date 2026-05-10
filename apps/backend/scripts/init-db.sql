-- Initialize DebateAI database
-- This script runs when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- These will be created by Prisma migrations, but we can add additional ones

-- Full-text search index for debate topics
CREATE INDEX IF NOT EXISTS idx_debates_topic_gin ON debates USING gin(to_tsvector('english', topic));

-- Index for message content search
CREATE INDEX IF NOT EXISTS idx_messages_content_gin ON messages USING gin(to_tsvector('english', content));

-- Index for fact check claims
CREATE INDEX IF NOT EXISTS idx_fact_checks_claim_gin ON fact_checks USING gin(to_tsvector('english', claim));

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_debates_user_status ON debates(user_id, status);
CREATE INDEX IF NOT EXISTS idx_messages_debate_created ON messages(debate_id, created_at);
CREATE INDEX IF NOT EXISTS idx_fact_checks_message ON fact_checks(message_id);

-- Enable necessary extensions for time-based queries
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET timezone = 'UTC';
