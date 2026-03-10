from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
from app.core.config import settings

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        now = datetime.utcnow()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(status_code=429, detail="Too many requests")
        
        # Add current request
        self.requests[client_ip].append(now)

rate_limiter = RateLimiter()
