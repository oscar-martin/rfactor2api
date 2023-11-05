from typing import Union
from fastapi import FastAPI
from rf2_data.sim_info_sync import SimInfoSync
import logging
import threading
from contextlib import asynccontextmanager
import model
import session

# Add logger
logger = logging.getLogger(__name__)
test_handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
logger.addHandler(test_handler)

info = SimInfoSync(logger=__name__)

def run_rfactor2_sharedmemory_reader():
    info.setMode(0) # optional, can be omitted
    info.setPID("") # optional, can be omitted
    info.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    _worker_thread = threading.Thread(target=run_rfactor2_sharedmemory_reader, daemon=False)
    _worker_thread.start()
    yield
    info.stop()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {}

@app.get("/healthz")
def healthz():
    return {"alive": True}

@app.get("/scoring/")
def read_scoring():
    return model.rF2Scoring.build(info.rf2Scor)

@app.get("/telemetry/")
def read_telemetry():
    return model.rF2Telemetry.build(info.rf2Tele)

@app.get("/running/")
def running():
    return { "active": not info._paused }

@app.get("/session/")
def read_session():
    return session.Session(model.rF2Scoring.build(info.rf2Scor), not info._paused)