-- Migration: News Graph System
-- Purpose: Create tables for linking related news articles and building story context
-- Date: 2025-10-19

-- News links table for connecting related news articles
CREATE TABLE IF NOT EXISTS news_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    news_id_1 UUID NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    news_id_2 UUID NOT NULL REFERENCES news(id) ON DELETE CASCADE,

    link_type VARCHAR(50) NOT NULL DEFAULT 'related', -- "continuation", "related", "opposite", "context"

    similarity_score FLOAT DEFAULT 0.0,
    semantic_distance FLOAT DEFAULT 0.0,

    keywords_overlap JSONB DEFAULT '{}',
    entities_overlap JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure we don't have duplicate links (both directions)
    CONSTRAINT no_duplicate_links CHECK (news_id_1 < news_id_2),
    UNIQUE(news_id_1, news_id_2)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_news_links_news_id_1 ON news_links(news_id_1);
CREATE INDEX IF NOT EXISTS idx_news_links_news_id_2 ON news_links(news_id_2);
CREATE INDEX IF NOT EXISTS idx_news_links_type ON news_links(link_type);
CREATE INDEX IF NOT EXISTS idx_news_links_similarity ON news_links(similarity_score DESC);

-- Digest drafts table for human-in-the-loop feedback
CREATE TABLE IF NOT EXISTS digest_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',

    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'published'
    reviewer_id UUID REFERENCES users(id),
    admin_feedback TEXT,
    admin_rating FLOAT CHECK (admin_rating >= 0 AND admin_rating <= 1),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,

    -- Track what was used to generate this draft
    category VARCHAR(50),
    style VARCHAR(50),
    persona_id VARCHAR(100),
    news_items_count INTEGER DEFAULT 0
);

-- Indexes for draft management
CREATE INDEX IF NOT EXISTS idx_digest_drafts_status ON digest_drafts(status);
CREATE INDEX IF NOT EXISTS idx_digest_drafts_reviewer ON digest_drafts(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_digest_drafts_created_at ON digest_drafts(created_at DESC);

-- Comments and notes
COMMENT ON TABLE news_links IS 'Links between related news articles for story context';
COMMENT ON COLUMN news_links.link_type IS 'Type of relationship: continuation, related, opposite, context';
COMMENT ON COLUMN news_links.similarity_score IS 'Numeric similarity score (0.0-1.0)';
COMMENT ON COLUMN news_links.keywords_overlap IS 'JSON of overlapping keywords between articles';
COMMENT ON COLUMN news_links.entities_overlap IS 'JSON of overlapping named entities';

COMMENT ON TABLE digest_drafts IS 'Draft digests for human review and feedback';
COMMENT ON COLUMN digest_drafts.status IS 'Review status: pending, approved, rejected, published';
COMMENT ON COLUMN digest_drafts.admin_rating IS 'Admin rating 0.0-1.0 for quality feedback';
