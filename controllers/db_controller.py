import asyncpg
import psycopg2

from constants.db_constants import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)

async def create_pool():
    return await asyncpg.create_pool(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )