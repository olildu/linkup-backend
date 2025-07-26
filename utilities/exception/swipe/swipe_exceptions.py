import functools
from fastapi import HTTPException, status
import psycopg2

from controllers.logger_controller import logger_controller
from controllers.db_controller import conn
from utilities.swipe.swipe_utilities import exists_in_queue

def handle_db_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs) 
        except psycopg2.Error as e:
            conn.rollback()
            logger_controller.error(f"Database error: {e}")

            if e.pgcode == 'P0001':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e).split('\n')[0]
                )
            elif e.pgcode == '23514':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot like/dislike yourself"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
    return wrapper

def assert_in_match_queue(liker_id, liked_id, cursor):
    if not exists_in_queue(liker_id, liked_id, cursor):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot like/dislike without liked_id in the match queue"
        )
