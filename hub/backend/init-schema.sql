-- Initialize database schema
-- This script runs automatically when PostgreSQL container is first created
-- It creates the base tables (excluding alembic_version which Flask-Migrate manages)

-- Create plants table
CREATE TABLE IF NOT EXISTS public.plants (
    id integer NOT NULL,
    nickname character varying(255),
    species character varying(255) NOT NULL
);

-- Create sequence for plants.id
CREATE SEQUENCE IF NOT EXISTS public.plants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Set sequence ownership
ALTER SEQUENCE public.plants_id_seq OWNED BY public.plants.id;

-- Set default value for id column
ALTER TABLE ONLY public.plants ALTER COLUMN id SET DEFAULT nextval('public.plants_id_seq'::regclass);

-- Add constraints (using DO block to check if they exist first)
DO $$
BEGIN
    -- Add primary key constraint if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'plants_pkey'
    ) THEN
        ALTER TABLE ONLY public.plants
            ADD CONSTRAINT plants_pkey PRIMARY KEY (id);
    END IF;
    
    -- Add unique constraint if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'plants_nickname_key'
    ) THEN
        ALTER TABLE ONLY public.plants
            ADD CONSTRAINT plants_nickname_key UNIQUE (nickname);
    END IF;
END $$;

-- Grant permissions to the database user
GRANT ALL PRIVILEGES ON TABLE public.plants TO growery_user;
GRANT ALL PRIVILEGES ON SEQUENCE public.plants_id_seq TO growery_user;

