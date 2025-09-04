-- Initialize PostgreSQL database for Smart Document Processing Platform

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database if not exists (this will be handled by POSTGRES_DB env var)
-- But we can create additional schemas or configurations here

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance (will be created by SQLAlchemy, but we can add custom ones)
-- These will be created after the tables are created by the application

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE document_processing TO postgres;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Note: Triggers for updated_at will be created by the application
-- This is just a placeholder for any custom database initialization
