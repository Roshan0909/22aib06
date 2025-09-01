from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta
import random
import string
from typing import Optional
import uvicorn
import requests

app = FastAPI()

urls = {}
clicks = {}

AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJuYWdhcm9zaGFuXzIyYWliMDZAa2draXRlLmFjLmluIiwiZXhwIjoxNzU2NzA0NjE0LCJpYXQiOjE3NTY3MDM3MTQsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiJkNjg5YzQzMC05NmI5LTQ2MzMtYmEzMy1lZTQxMmQyMDQ4ZGQiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJuYWdhcm9zaGFuIG5zIiwic3ViIjoiNzI4MzZiYzUtMjA3NS00MDEyLTg5ZjUtN2ViNjZkNGFkZjNiIn0sImVtYWlsIjoibmFnYXJvc2hhbl8yMmFpYjA2QGtna2l0ZS5hYy5pbiIsIm5hbWUiOiJuYWdhcm9zaGFuIG5zIiwicm9sbE5vIjoiMjJhaWIwNiIsImFjY2Vzc0NvZGUiOiJkcVh1d1oiLCJjbGllbnRJRCI6IjcyODM2YmM1LTIwNzUtNDAxMi04OWY1LTdlYjY2ZDRhZGYzYiIsImNsaWVudFNlY3JldCI6IndRYXdtdE5ITldEU1pBTnIifQ.jKO6vDr_KZ3MLpBJUvAcPOjP-ioyQiOdhdvv0TJBizs"
LOG_URL = "http://20.244.56.144/evaluation-service/logs"

def log_msg(stack, level, package, message):
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }
    
    try:
        response = requests.post(LOG_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"[{datetime.now().isoformat()}] LOG_SUCCESS: {message}")
        else:
            print(f"[{datetime.now().isoformat()}] LOG_ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] LOG_ERROR: {str(e)}")

@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_msg("backend", "info", "middleware", f"Request: {request.method} {request.url}")
    response = await call_next(request)
    log_msg("backend", "info", "middleware", f"Response: {response.status_code}")
    return response

class UrlRequest(BaseModel):
    url: HttpUrl
    validity: Optional[int] = 30
    shortcode: Optional[str] = None

def make_code():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

@app.post("/shortUrls", status_code=201)
async def create_short_url(request: UrlRequest, req: Request):
    log_msg("backend", "info", "handler", f"Creating short URL for: {request.url}")
    
    if not str(request.url).startswith(('http://', 'https://')):
        log_msg("backend", "error", "handler", f"Invalid URL format: {request.url}")
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    if request.shortcode:
        if request.shortcode in urls:
            log_msg("backend", "error", "handler", f"Shortcode already exists: {request.shortcode}")
            raise HTTPException(status_code=409, detail="Shortcode exists")
        code = request.shortcode
    else:
        while True:
            code = make_code()
            if code not in urls:
                break
    
    expire_time = datetime.now() + timedelta(minutes=request.validity)
    
    urls[code] = {
        "original_url": str(request.url),
        "created_at": datetime.now().isoformat(),
        "expiry": expire_time.isoformat(),
        "hits": 0,
        "clicks": []
    }
    
    host = req.headers.get("host", "localhost:8001")
    shortlink = f"http://{host}/{code}"
    
    log_msg("backend", "info", "service", f"Short URL created: {code} -> {request.url}")
    
    return {
        "shortlink": shortlink,
        "expiry": expire_time.isoformat()
    }

@app.get("/shortUrls/{shortcode}")
async def get_stats(shortcode: str):
    log_msg("backend", "info", "handler", f"Getting stats for shortcode: {shortcode}")
    
    if shortcode not in urls:
        log_msg("backend", "warn", "handler", f"Shortcode not found: {shortcode}")
        raise HTTPException(status_code=404, detail="Not found")
    
    url_data = urls[shortcode]
    
    log_msg("backend", "info", "service", f"Stats retrieved for {shortcode}: {url_data['hits']} clicks")
    
    return {
        "shortcode": shortcode,
        "original_url": url_data["original_url"],
        "created_at": url_data["created_at"],
        "expiry": url_data["expiry"],
        "total_clicks": url_data["hits"],
        "clicks": url_data["clicks"]
    }

@app.get("/{shortcode}")
async def redirect(shortcode: str, request: Request):
    log_msg("backend", "info", "handler", f"Redirect request for shortcode: {shortcode}")
    
    if shortcode not in urls:
        log_msg("backend", "warn", "handler", f"Shortcode not found: {shortcode}")
        raise HTTPException(status_code=404, detail="Not found")
    
    url_data = urls[shortcode]
    
    expire_time = datetime.fromisoformat(url_data["expiry"])
    if datetime.now() > expire_time:
        log_msg("backend", "warn", "handler", f"Shortcode expired: {shortcode}")
        raise HTTPException(status_code=410, detail="Expired")
    
    url_data["hits"] += 1
    click_record = {
        "timestamp": datetime.now().isoformat(),
        "referrer": request.headers.get("referer", "direct"),
        "location": "IN"
    }
    url_data["clicks"].append(click_record)
    
    log_msg("backend", "info", "service", f"Redirecting {shortcode} to {url_data['original_url']}")
    
    return RedirectResponse(url=url_data["original_url"])

if __name__ == "__main__":
    log_msg("backend", "info", "service", "Starting URL Shortener Microservice")
    uvicorn.run(app, host="0.0.0.0", port=8001)
