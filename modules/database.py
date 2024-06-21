import asyncmy
import logging
from dotenv import load_dotenv
from config import settings

load_dotenv()

# Logger 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_HOST = "10.17.37.35"
DATABASE_PORT = 3306
DATABASE_SCHEMA = "db_operator"

# Construct the DSN (Data Source Name)
DATABASE_URL = f"mysql://{settings.mysql_user}:{settings.mysql_password}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_SCHEMA}"


class Database:
    def __init__(self, dsn):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        if self.pool is None:
            self.pool = await asyncmy.create_pool(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                user=settings.mysql_user,
                password=settings.mysql_password,
                db=DATABASE_SCHEMA,
                minsize=1,
                maxsize=5,
                autocommit=True
            )
            logger.info("Database connection pool created.")
        return self.pool

    async def disconnect(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            logger.info("Database connection pool closed.")

    async def fetch_one(self, query, *args):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, args)
                result = await cursor.fetchone()
                if result:
                    return dict(zip([desc[0] for desc in cursor.description], result))
                return None

    async def execute(self, query, *args):
        async with self.pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(query, args)
                await connection.commit()
                return cursor


database = Database(DATABASE_URL)


async def get_db():
    if not database.pool:
        await database.connect()
    return database
