# INIT
import logging
from typing import Optional, List

from fastapi import HTTPException, Depends
from functools import lru_cache
from starlette.requests import Request

from src.app.App import *
from src.pipelines.Controller import Controller
from src.pipelines.Options import index_filename
from src.pipelines.UpdateModel import run, fit
from src.app.Types import Matches, Query, Embed, Profile

import config
from src.utils.helper.timer import time_execute


@lru_cache()
def get_settings():
    try:
        return config.Settings()
    except Exception as e:
        logging.info('Could not init config file.')


@app.get("/ping", tags=["health"])
@limiter.limit("100/minute")
async def ping(request: Request):
    return 'pong'


@app.get("/run/model/update", tags=["pipeline"])
@limiter.limit("3/minute")
async def run_model(request: Request, num_limit: Optional[int] = 1000, num_trees: Optional[int] = 100, settings: config.Settings = Depends(get_settings)):
    try:
        return time_execute(lambda: run(settings, num_limit, num_trees), "Run Model")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/run/model/fit", tags=["pipeline"])
@limiter.limit("3/minute")
async def run_model(request: Request, settings: config.Settings = Depends(get_settings)):
    try:
        return time_execute(lambda: fit(settings), "Run Fit")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run/profile/update", response_model=Profile, tags=["pipeline"])
@limiter.limit("100/minute")
async def run_profile_update(request: Request, ids: List, settings: config.Settings = Depends(get_settings)):
    try:
        return Controller.embed_by_ids(settings.BIG_QUERY_CERT, ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/by-embed", response_model=Matches, tags=["pipeline"])
@limiter.limit("100/minute")
async def query(request: Request, embed: Embed, num_limit: Optional[int] = 100):
    try:
        return Controller.embed_query(index_filename, embed.embed, num_limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/by-attributes", response_model=Matches, tags=["pipeline"])
@limiter.limit("100/minute")
async def query(request: Request, properties: Query, num_limit: Optional[int] = 100):
    try:
        return Controller.attributes_query(index_filename, properties, num_limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

