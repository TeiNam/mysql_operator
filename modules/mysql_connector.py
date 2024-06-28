import asyncmy
from typing import AsyncGenerator
from config import DB_CONFIG


async def get_db_connection() -> AsyncGenerator:
    conn = await asyncmy.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        await conn.close()


class MySQLConnector:
    @staticmethod
    async def execute_query(query: str, params: tuple = None):
        async with await asyncmy.connect(**DB_CONFIG) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                return cursor.lastrowid

    @staticmethod
    async def fetch_one(query: str, params: tuple = None):
        async with await asyncmy.connect(**DB_CONFIG) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchone()

    @staticmethod
    async def fetch_all(query: str, params: tuple = None):
        async with await asyncmy.connect(**DB_CONFIG) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()
