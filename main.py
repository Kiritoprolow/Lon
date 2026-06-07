from fastapi import FastAPI, Request
from supabase import create_client
import threading, httpx, time, re
from datetime import datetime, timezone

SUPABASE_URL = "https://tlvxpsqefouumvfdihbs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRsdnhwc3FlZm91dW12ZmRpaGJzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAxODc1MDYsImV4cCI6MjA5NTc2MzUwNn0.2oYQQ2dOzH9i0W7wfYmJaostwqJj1MZCQl_ruG-HTUs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def keep_alive():
    while True:
        time.sleep(600)
        try:
            httpx.get("https://lon-lmis.onrender.com/health")
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "alive"}

def parse_list(val: str) -> list[str]:
    """Tách theo dòng và dấu phẩy, bỏ item rỗng"""
    items = []
    for line in val.splitlines():
        for part in line.split(","):
            clean = part.strip().strip("`").strip()
            if clean:
                items.append(clean)
    return items

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    try:
        embeds = data.get("embeds", [{}])
        desc   = embeds[0].get("description", "")
        fields = embeds[0].get("fields", [])

        u  = re.search(r'Username\s*:\s*([^\s,\n]+)', desc)
        l  = re.search(r'Level\s*:\s*(\d+)', desc)
        rc = re.search(r'Race\s*:\s*([^\n,]+?)(?:\s*,|\s*\n|$)', desc)
        fr = re.search(r'Fruits\s*:\s*([^\n]+?)(?:\s*\n|$)', desc)

        username = u.group(1).strip() if u else "Unknown"
        level    = int(l.group(1)) if l else 0
        race     = rc.group(1).strip() if rc else "Unknown"
        fruit    = fr.group(1).strip() if fr else "None"

        inv_fruit = ""
        melee     = ""
        inventory = ""

        for f in fields:
            name = f.get("name", "")
            val  = f.get("value", "").strip().strip("`").strip()

            if "Inventory Fruit" in name:
                inv_fruit = val
            elif "Melee" in name:
                # Lưu TẤT CẢ melee, join bằng dấu phẩy
                parts = parse_list(val)
                melee = ", ".join(parts)
            elif "Inventory" in name:
                parts = parse_list(val)
                inventory = ", ".join(parts)

        now = datetime.now(timezone.utc).isoformat()

        supabase.table("player_stats").upsert({
            "username":         username,
            "level":            level,
            "race":             race,
            "fruit":            fruit,
            "inventory_fruits": inv_fruit,
            "melee":            melee,
            "inventory":        inventory,
            "status":           "online",
            "updated_at":       now,
            "last_seen":        now,
        }, on_conflict="username").execute()

        return {"status": "ok", "username": username}
    except Exception as e:
        return {"error": str(e)}
        
