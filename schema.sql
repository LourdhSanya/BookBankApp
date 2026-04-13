-- ============================================================
-- Book Bank Management System – Supabase Schema (Normalized)
-- Run this ONCE in Supabase SQL Editor:
-- https://supabase.com/dashboard/project/mkpaimtgfwgwqbobszqs/sql/new
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    user_id   SERIAL PRIMARY KEY,
    username  TEXT NOT NULL UNIQUE,
    password  TEXT NOT NULL,
    name      TEXT NOT NULL,
    role      TEXT NOT NULL CHECK(role IN ('student', 'librarian'))
);

CREATE TABLE IF NOT EXISTS books (
    book_id   SERIAL PRIMARY KEY,
    book_name TEXT NOT NULL,
    author    TEXT NOT NULL DEFAULT 'Unknown',
    status    TEXT NOT NULL DEFAULT 'Available'
                   CHECK(status IN ('Available', 'Issued', 'Reserved'))
);

CREATE TABLE IF NOT EXISTS issues (
    issue_id    SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    book_id     INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    issue_date  DATE    NOT NULL,
    due_date    DATE    NOT NULL,
    return_date DATE,
    fine        NUMERIC(10,2) DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id   SERIAL PRIMARY KEY,
    book_id          INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    user_id          INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    reservation_date DATE    NOT NULL
);
