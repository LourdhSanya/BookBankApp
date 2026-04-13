-- ============================================================
-- Migration 001 – Normalize reservations & fix column types
-- Run this in the Supabase SQL Editor ONCE:
-- https://supabase.com/dashboard/project/mkpaimtgfwgwqbobszqs/sql/new
-- ============================================================

-- 1. Remove redundant columns from reservations
ALTER TABLE reservations DROP COLUMN IF EXISTS book_name;
ALTER TABLE reservations DROP COLUMN IF EXISTS username;

-- 2. Convert date columns from TEXT to DATE
--    (Only needed if they are currently TEXT — safe to re-run)
ALTER TABLE issues
    ALTER COLUMN issue_date  TYPE DATE USING issue_date::DATE,
    ALTER COLUMN due_date    TYPE DATE USING due_date::DATE,
    ALTER COLUMN return_date TYPE DATE USING return_date::DATE;

ALTER TABLE reservations
    ALTER COLUMN reservation_date TYPE DATE USING reservation_date::DATE;

-- 3. Convert fine from REAL to NUMERIC(10,2)
ALTER TABLE issues
    ALTER COLUMN fine TYPE NUMERIC(10,2) USING fine::NUMERIC(10,2);
