from fastapi import FastAPI, Request
import httpx, time, threading, re
from datetime import datetime

SUPABASE_URL = "https://tlvxpsqefouumvfdihbs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRsdnhwc3FlZm91dW12ZmRpaGJzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAxODc1MDYsImV4cCI6MjA5NTc2MzUwNn0.2oYQQ2dOzH9i0W7wfYmJaostwqJj1MZCQl_ruG-HTUs"

def keep_alive():
    while True:
        time.sleep(600)
        try:
            httpx.get("https://lon-lmis.onrender.com/")
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    try:
        embeds = data.get("embeds", [{}])
        desc = embeds[0].get("description", "")
        fields = embeds[0].get("fields", [])

        u = re.search(r'Username\s*:\s*(\S+)', desc)
        l = re.search(r'Level\s*:\s*(\d+)', desc)
        rc = re.search(r'Race\s*:\s*(.+?)(?:,|\n|$)', desc)
        fr = re.search(r'Fruits\s*:\s*(.+?)(?:\n|$)', desc)

        username = u.group(1) if u else "Unknown"
        level = int(l.group(1)) if l else 0
        race = rc.group(1).strip() if rc else "Unknown"
        fruit = fr.group(1).strip() if fr else "None"

        inv_fruit = ""
        for f in fields:
            name = f.get("name", "")
            val = f.get("value", "").strip().strip("`").strip()
            if "Inventory Fruit" in name:
                inv_fruit = val

        now = datetime.utcnow().isoformat()

        httpx.post(
            SUPABASE_URL + "/rest/v1/player_stats",
            json={
                "username": username,
                "level": level,
                "race": race,
                "fruit": fruit,
                "inventory_fruits": inv_fruit,
                "status": "online",
                "updated_at": now,
                "last_seen": now,
            },
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": "Bearer " + SUPABASE_KEY,
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=minimal",
            }
        )

        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}
        
