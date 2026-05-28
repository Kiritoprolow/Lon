from fastapi import FastAPI
from pydantic import BaseModel
import httpx, time, threading

def keep_alive():
    while True:
        time.sleep(600)
        try:
            httpx.get("https://lon-lmis.onrender.com/")
        except:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

app = FastAPI()

SOLVEX_KEY = "sk_f7bje7s050kv4x92ea34z6g2w8tvq99m"

class SolveRequest(BaseModel):
    username: str = ""
    cookie: str = ""

@app.post("/api/solve-account")
def solve(body: SolveRequest):
    t = httpx.post("https://api.solvex.run/createTask", json={
        "clientKey": SOLVEX_KEY,
        "task": {
            "type": "FunCaptchaTask",
            "websiteURL": "https://roblox.com",
            "websitePublicKey": "476068BF-9607-4799-B53D-966BE98E2B81",
            "proxyType": "http",
            "proxyAddress": "142.111.67.146",
            "proxyPort": 5611,
            "proxyLogin": "oiblryuw",
            "proxyPassword": "vrmgep3awfb9",
            "cookies": body.cookie,
        }
    }, timeout=30).json()

    task_id = t.get("taskId")
    if not task_id:
        return {"error": t}

    for _ in range(60):
        r = httpx.post("https://api.solvex.run/getTaskResult", json={
            "clientKey": SOLVEX_KEY,
            "taskId": task_id,
        }, timeout=30).json()
        if r.get("status") == "ready":
            return {"token": r["solution"]["token"]}
        time.sleep(0.5)

    return {"error": "timeout"}
