import sqlite3
import os

DB_PATH = "prisma/dev.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create User table
    c.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            stripeId TEXT,
            searchCount INTEGER DEFAULT 0,
            plan TEXT DEFAULT 'FREE',
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Shop table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Shop (
            id TEXT PRIMARY KEY,
            name TEXT,
            url TEXT UNIQUE,
            optOut BOOLEAN DEFAULT 0,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Product table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Product (
            id TEXT PRIMARY KEY,
            shopId TEXT,
            title TEXT,
            price INTEGER,
            thumbnailUrl TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(shopId) REFERENCES Shop(id)
        )
    ''')

    # Create Image table
    c.execute('''
        CREATE TABLE IF NOT EXISTS Image (
            id TEXT PRIMARY KEY,
            productId TEXT,
            imageUrl TEXT,
            vectorId TEXT,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(productId) REFERENCES Product(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized (SQLite).")
