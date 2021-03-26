from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
    "https://api200.herokuapp.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:4000",
    "https://localhost:3000",
    "https://localhost:8080",
    "http://localhost:8080",
    "https://localhost:4000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="http*://localhost*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
