-- Create vector extension (if not exists)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create emails table
CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    subject TEXT NOT NULL,
    from_address TEXT NOT NULL,
    date TEXT,
    plain_text TEXT,
    html_content TEXT,
    attachments JSONB,
    embedding VECTOR(384),  -- Dimension of the embedding vector (adjust as needed)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create classifications table
CREATE TABLE IF NOT EXISTS classifications (
    id SERIAL PRIMARY KEY,
    email_id INTEGER NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    request_type TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    is_duplicate BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create extractions table
CREATE TABLE IF NOT EXISTS extractions (
    id SERIAL PRIMARY KEY,
    email_id INTEGER NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    amount TEXT,
    reference_number TEXT,
    account_number TEXT,
    extracted_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    email_id INTEGER NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    report_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS emails_created_at_idx ON emails(created_at);
CREATE INDEX IF NOT EXISTS classifications_email_id_idx ON classifications(email_id);
CREATE INDEX IF NOT EXISTS classifications_request_type_idx ON classifications(request_type);
CREATE INDEX IF NOT EXISTS extractions_email_id_idx ON extractions(email_id);
CREATE INDEX IF NOT EXISTS reports_email_id_idx ON reports(email_id);
CREATE INDEX IF NOT EXISTS reports_report_type_idx ON reports(report_type);

-- Create vector index for similarity search
CREATE INDEX IF NOT EXISTS emails_embedding_idx ON emails USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- Number of lists, adjust based on data size