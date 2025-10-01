-- Database initialization schema for Amarsite.Online Study Platform
-- This SQL script creates all necessary tables for the application

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Study sets table
CREATE TABLE IF NOT EXISTS study_sets (
    id VARCHAR(36) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    subject VARCHAR(100),
    is_public BOOLEAN DEFAULT FALSE,
    share_code VARCHAR(20) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Cards table
CREATE TABLE IF NOT EXISTS cards (
    id SERIAL PRIMARY KEY,
    study_set_id VARCHAR(36) NOT NULL REFERENCES study_sets(id) ON DELETE CASCADE,
    term TEXT NOT NULL,
    definition TEXT NOT NULL,
    term_image_url TEXT,
    definition_image_url TEXT,
    card_order INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Study progress table (for spaced repetition tracking)
CREATE TABLE IF NOT EXISTS study_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    study_set_id VARCHAR(36) NOT NULL REFERENCES study_sets(id) ON DELETE CASCADE,
    mastery_level INTEGER DEFAULT 0,
    times_studied INTEGER DEFAULT 0,
    last_studied TIMESTAMP,
    difficulty_history JSONB DEFAULT '[]'::jsonb,
    next_review_date TIMESTAMP,
    easiness_factor DECIMAL(3,2) DEFAULT 2.5,
    repetitions INTEGER DEFAULT 0,
    interval_days INTEGER DEFAULT 0,
    UNIQUE(user_id, card_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_study_sets_user_id ON study_sets(user_id);
CREATE INDEX IF NOT EXISTS idx_study_sets_is_public ON study_sets(is_public);
CREATE INDEX IF NOT EXISTS idx_study_sets_share_code ON study_sets(share_code);
CREATE INDEX IF NOT EXISTS idx_cards_study_set_id ON cards(study_set_id);
CREATE INDEX IF NOT EXISTS idx_study_progress_user_id ON study_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_study_progress_card_id ON study_progress(card_id);
CREATE INDEX IF NOT EXISTS idx_study_progress_next_review ON study_progress(next_review_date);
