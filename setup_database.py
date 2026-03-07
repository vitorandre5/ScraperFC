#!/usr/bin/env python3
"""Script to create database tables in Supabase self-hosted."""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
# Self-hosted Supabase at localhost
DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "1zqGQjBi6rCNi06zw2Gl5aLG90qrQep8"

# SQL Script
SQL_SCRIPT = """
-- ScraperFC Database Schema
-- Create all tables

-- 1. SPORTS table
CREATE TABLE IF NOT EXISTS sports (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_sports_key ON sports(key);

-- 2. LEAGUES table
CREATE TABLE IF NOT EXISTS leagues (
    id SERIAL PRIMARY KEY,
    sport_id INTEGER NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    country VARCHAR(100),
    canonical_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_league_sport_canonical UNIQUE(sport_id, canonical_name)
);

CREATE INDEX IF NOT EXISTS ix_leagues_sport_canonical ON leagues(sport_id, canonical_name);
CREATE INDEX IF NOT EXISTS ix_leagues_country ON leagues(country);

-- 3. TEAMS table
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    sport_id INTEGER NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    canonical_name VARCHAR(200) NOT NULL,
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_team_sport_canonical UNIQUE(sport_id, canonical_name)
);

CREATE INDEX IF NOT EXISTS ix_teams_sport_canonical ON teams(sport_id, canonical_name);

-- 4. MATCHES table
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    sport_id INTEGER NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    league_id INTEGER NOT NULL REFERENCES leagues(id) ON DELETE CASCADE,
    season VARCHAR(50),
    home_team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    away_team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    match_datetime_utc TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    source_primary VARCHAR(50) NOT NULL,
    source_external_id VARCHAR(100),
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_match_unique_game UNIQUE(league_id, home_team_id, away_team_id, match_datetime_utc)
);

CREATE INDEX IF NOT EXISTS ix_matches_datetime ON matches(match_datetime_utc);
CREATE INDEX IF NOT EXISTS ix_matches_status ON matches(status);
CREATE INDEX IF NOT EXISTS ix_matches_league ON matches(league_id);
CREATE INDEX IF NOT EXISTS ix_matches_home_team ON matches(home_team_id);
CREATE INDEX IF NOT EXISTS ix_matches_away_team ON matches(away_team_id);
CREATE INDEX IF NOT EXISTS ix_matches_source ON matches(source_primary, source_external_id);

-- 5. EXTERNAL_MAPPINGS table
CREATE TABLE IF NOT EXISTS external_mappings (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    source VARCHAR(50) NOT NULL,
    external_id VARCHAR(200) NOT NULL,
    league_id INTEGER REFERENCES leagues(id) ON DELETE CASCADE,
    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_external_mapping UNIQUE(entity_type, source, external_id)
);

CREATE INDEX IF NOT EXISTS ix_external_entity ON external_mappings(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS ix_external_source ON external_mappings(source, external_id);

-- 6. SYNC_RUNS table
CREATE TABLE IF NOT EXISTS sync_runs (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    source VARCHAR(50),
    matches_created INTEGER DEFAULT 0,
    matches_updated INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_sync_runs_started ON sync_runs(started_at);
CREATE INDEX IF NOT EXISTS ix_sync_runs_status ON sync_runs(status);

-- Insert initial data
INSERT INTO sports (key, name) VALUES ('football', 'Football') ON CONFLICT (key) DO NOTHING;
"""

def main():
    """Main function to create tables."""
    try:
        print(f"🔌 Conectando ao Supabase...")
        print(f"   Host: {DB_HOST}")
        print(f"   Port: {DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=10
        )
        
        print("✅ Conectado com sucesso!")
        
        # Create cursor
        cursor = conn.cursor()
        
        print("\n📝 Executando script SQL...")
        
        # Execute SQL script
        cursor.execute(SQL_SCRIPT)
        
        # Commit changes
        conn.commit()
        
        print("✅ Script SQL executado com sucesso!")
        
        # Verify tables
        print("\n🔍 Verificando tabelas criadas...")
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        
        tables = cursor.fetchall()
        print(f"\n✅ {len(tables)} tabelas criadas:")
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Banco de dados configurado com sucesso!")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão: {e}")
        print("\nVerifique:")
        print("  - O Supabase está rodando?")
        print("  - Host correto: 127.0.0.1")
        print("  - Porta correta: 5432")
        print("  - Credenciais corretas")
        
    except psycopg2.Error as e:
        print(f"❌ Erro SQL: {e}")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
