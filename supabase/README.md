# Supabase Setup

This folder contains everything needed to provision the ScraperFC schema directly on Supabase.

## Structure

- `config.toml`: Supabase CLI project configuration
- `migrations/20260306153000_init_scraperfc.sql`: Initial schema migration
- `seed.sql`: Initial seed data (`football` sport)

## Apply in Supabase SQL Editor

1. Open your project in Supabase.
2. Go to `SQL Editor`.
3. Run the SQL from `migrations/20260306153000_init_scraperfc.sql`.
4. Run `seed.sql`.

## Apply with Supabase CLI

1. Install Supabase CLI.
2. Login:
   ```bash
   supabase login
   ```
3. Link this repo to your project:
   ```bash
   supabase link --project-ref kkfbwquqzoxjtwakfpsg
   ```
4. Push migrations:
   ```bash
   supabase db push
   ```
5. Run seed file:
   ```bash
   supabase db reset --linked
   ```

## Required runtime env

Use this value in your deployment environment:

```env
DATABASE_URL=postgresql://postgres:Mar1aLu1sa2022%40@db.kkfbwquqzoxjtwakfpsg.supabase.co:5432/postgres
```
