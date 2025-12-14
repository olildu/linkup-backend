import asyncio
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from contextlib import asynccontextmanager

from app.controllers.db_controller import create_pool
from app.routes.chats.chats_endpoints import chats_router
from app.routes.actions.swipe_endpoint import swipe_route 
from app.routes.matches.matches_endpoint import matches_router
from app.routes.user.get_user_data import user_router
from app.routes.auth.auth_endpoints import auth_router
from app.routes.common.common_endpoints import common_router
from app.routes.cities.cities_endpoints import location_router

from app.routes.chats.chat_websocket_endpoints import chatsocket_router
from app.routes.matches.connections_websocket_endpoints import connectionsocket_router
from app.routes.matches.lobby.lobby_websocket_endpoints import lobbysocket_router, start_waiting_period

ist = timezone("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=ist)

loop = asyncio.get_event_loop()

def start_meet_at_8_sync():
    asyncio.run_coroutine_threadsafe(start_waiting_period(), loop)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create asyncpg pool
    app.state.db_pool = await create_pool()

    # Setup APScheduler job
    trigger = CronTrigger(hour=20, minute=0, timezone=ist)
    scheduler.add_job(start_meet_at_8_sync, trigger)
    scheduler.start()

    yield

    # Shutdown scheduler and close pool
    scheduler.shutdown()
    await app.state.db_pool.close()
    
app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(swipe_route)
app.include_router(matches_router)
app.include_router(chats_router)
app.include_router(common_router)
app.include_router(location_router)

app.include_router(chatsocket_router) 
app.include_router(lobbysocket_router)
app.include_router(connectionsocket_router)