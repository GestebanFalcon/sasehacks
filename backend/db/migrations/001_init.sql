CREATE EXTENSION IF NOT EXISTS vector;


CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_created_at ON sessions (created_at);

CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    content TEXT,
    embedding VECTOR(384),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_reviews_session_id ON reviews (session_id);

CREATE TABLE IF NOT EXISTS messages(
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    content TEXT NOT NULL,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_session_id ON messages (session_id);