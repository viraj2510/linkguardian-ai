from contextlib import asynccontextmanager
import logging
import os
from urllib.parse import urlsplit, urlunsplit
import ipaddress
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from .model import analyze_url, load_model

logger = logging.getLogger(__name__)

class UrlPayload(BaseModel):
    url: str = Field(min_length=1, max_length=4096)

    @field_validator('url')
    @classmethod
    def normalize_url(cls, value):
        value = value.strip()
        if not value or re.search(r'[\s\x00-\x1f\x7f]', value):
            raise ValueError('Enter a URL without spaces or control characters.')
        if '://' not in value:
            if re.match(r'^[a-zA-Z][\w+.-]*:', value) and not re.match(r'^[^/:]+:\d+(?:/|$)', value):
                raise ValueError('Only HTTP and HTTPS URLs are supported.')
            value = 'https://' + value
        try:
            parts = urlsplit(value)
            if parts.scheme.lower() not in ('http', 'https') or not parts.hostname:
                raise ValueError('Enter a valid HTTP or HTTPS URL.')
            if parts.username is not None or parts.password is not None:
                raise ValueError('URLs containing embedded credentials are not supported.')
            host = parts.hostname.encode('idna').decode('ascii').lower().rstrip('.')
            port = parts.port
            try:
                ip = ipaddress.ip_address(host)
                if not ip.is_global:
                    raise ValueError('Enter a public website address.')
                authority = '[' + host + ']' if ip.version == 6 else host
            except ValueError as exc:
                if 'public website' in str(exc):
                    raise
                if '.' not in host or len(host) > 253 or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in host.split('.')) or host.endswith(('.local', '.localhost', '.internal')):
                    raise ValueError('Enter a valid public domain name.')
                authority = host
            if port is not None:
                authority += ':' + str(port)
            return urlunsplit((parts.scheme.lower(), authority, parts.path, parts.query, parts.fragment))
        except (ValueError, UnicodeError) as exc:
            raise ValueError(str(exc)) from exc

@asynccontextmanager
async def lifespan(app):
    try:
        load_model()
    except Exception:
        logger.exception('Model could not be loaded; scans will use heuristic analysis.')
    yield

app = FastAPI(title='LinkGuardian API', version='0.2.0', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',') if origin.strip()],
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type'],
)

@app.get('/health')
def health():
    try:
        load_model()
        available = True
    except Exception:
        available = False
    return {'status': 'ok' if available else 'degraded', 'model_available': available}

@app.post('/predict')
def get_prediction(payload: UrlPayload):
    try:
        return {'url': payload.url, **analyze_url(payload.url)}
    except Exception as exc:
        logger.exception('URL analysis failed')
        raise HTTPException(status_code=503, detail='Analysis is temporarily unavailable. Please try again.') from exc
