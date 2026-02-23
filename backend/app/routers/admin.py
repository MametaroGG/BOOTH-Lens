from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_db_connection

router = APIRouter()

class OptOutRequest(BaseModel):
    shopUrl: str

@router.post("/opt-out")
async def request_opt_out(req: OptOutRequest):
    if "booth.pm" not in req.shopUrl:
        raise HTTPException(status_code=400, detail="Invalid BOOTH URL")
    
    # Extract shop name or use URL
    identifier = req.shopUrl
    if ".booth.pm" in identifier:
        try:
            identifier = identifier.split("://")[-1].split(".booth.pm")[0]
        except:
            pass

    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Upsert Shop with optOut=1
        # Check if exists
        c.execute("SELECT id FROM Shop WHERE url = ?", (req.shopUrl,))
        row = c.fetchone()
        if row:
            c.execute("UPDATE Shop SET optOut = 1 WHERE id = ?", (row['id'],))
        else:
             import uuid
             shop_id = str(uuid.uuid4())
             c.execute("INSERT INTO Shop (id, name, url, optOut) VALUES (?, ?, ?, 1)", 
                       (shop_id, identifier, req.shopUrl))
        conn.commit()
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    
    return {"status": "success", "message": "Opt-out request received"}
