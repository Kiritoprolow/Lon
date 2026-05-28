from fastapi import FastAPI, Query
import httpx, time

app = FastAPI()

YESCAPTCHA_KEY = "ed0e63b5afe16439765adca97707ce93b5d04d42124299"  # thay key của mày vào đây
MY_API_KEY = "hainguyen13122011"  # tự đặt password để bảo vệ endpoint

@app.get("/api/solve-account")
def solve(api_key: str = Query(...)):
    if api_key != MY_API_KEY:
        return {"error": "unauthorized"}

    # Tạo task
    t = httpx.post("https://api.yescaptcha.com/createTask", json={
        "clientKey": YESCAPTCHA_KEY,
        "task": {
            "type": "FunCaptchaTaskProxyless",
            "websiteURL": "https://roblox.com",
            "websitePublicKey": "476068BF-9607-4799-B53D-966BE98E2B81",
        }
    }, timeout=30).json()

    task_id = t.get("taskId")
    if not task_id:
        return {"error": t}

    # Poll kết quả
    for _ in range(60):
        r = httpx.post("https://api.yescaptcha.com/getTaskResult", json={
            "clientKey": YESCAPTCHA_KEY,
            "taskId": task_id,
        }, timeout=30).json()
        if r.get("status") == "ready":
            return {"token": r["solution"]["token"]}
        time.sleep(0.5)

    return {"error": "timeout"}