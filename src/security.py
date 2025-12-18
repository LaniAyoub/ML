"""
Security middleware and utilities for production API
"""
from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
from typing import Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# API Key Header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> Optional[str]:
    """
    Verify API key for authenticated endpoints.
    Returns the API key if valid, raises HTTPException if invalid.
    """
    # Check if API key authentication is enabled
    if not os.getenv("API_KEY_ENABLED", "false").lower() == "true":
        return None
    
    # Get the expected API key from environment
    expected_key = os.getenv("API_KEY")
    
    if not expected_key:
        logger.error("API_KEY not configured but API_KEY_ENABLED is true")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error"
        )
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != expected_key:
        logger.warning(f"Invalid API key attempt from {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return api_key


class SecurityHeaders:
    """Middleware to add security headers to all responses."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Add security headers
                security_headers = {
                    b"x-content-type-options": b"nosniff",
                    b"x-frame-options": b"DENY",
                    b"x-xss-protection": b"1; mode=block",
                    b"strict-transport-security": b"max-age=31536000; includeSubDomains",
                    b"content-security-policy": b"default-src 'self'",
                }
                
                headers.update(security_headers)
                message["headers"] = [(k, v) for k, v in headers.items()]
            
            await send(message)
        
        await self.app(scope, receive, send_with_security_headers)


def hash_sensitive_data(data: str) -> str:
    """
    Hash sensitive data for logging purposes.
    
    Args:
        data: Sensitive string to hash
        
    Returns:
        SHA256 hash of the data
    """
    return hashlib.sha256(data.encode()).hexdigest()[:16]


class RequestLogger:
    """Middleware to log all requests with timing information."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = datetime.now()
        
        async def send_with_logging(message):
            if message["type"] == "http.response.start":
                duration = (datetime.now() - start_time).total_seconds()
                status_code = message["status"]
                
                logger.info(
                    f"{scope['method']} {scope['path']} "
                    f"completed with {status_code} in {duration:.3f}s"
                )
            
            await send(message)
        
        await self.app(scope, receive, send_with_logging)


def setup_security(app):
    """
    Setup security features for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Add rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add security headers middleware
    app.add_middleware(SecurityHeaders)
    
    # Add request logging middleware
    app.add_middleware(RequestLogger)
    
    logger.info("Security features initialized")
