from fastapi import Depends, HTTPException
from typing import Optional
from .db import get_db_connection
import sqlite3

# Simple mock user dependency for now
async def get_current_user_id():
    return "demo-user-id" 

async def check_search_limit(user_id: str = Depends(get_current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM User WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()

        if not user_row:
            # Create user if not exists
            cursor.execute("INSERT INTO User (id, email, plan, searchCount) VALUES (?, ?, ?, ?)", 
                           (user_id, "demo@example.com", "FREE", 0))
            conn.commit()
            cursor.execute("SELECT * FROM User WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
        
        # Convert row to dict for easier access
        user = dict(user_row)

        # By-pass search limit for demo user during development/testing
        if user['plan'] == "FREE" and user['searchCount'] >= 3 and user_id != "demo-user-id":
             conn.close()
             raise HTTPException(status_code=403, detail="Free plan limit reached (3 searches/month). Please upgrade.")
        
        # Increment search count
        cursor.execute("UPDATE User SET searchCount = searchCount + 1 WHERE id = ?", (user_id,))
        conn.commit()
        
        return user
    finally:
        conn.close()
