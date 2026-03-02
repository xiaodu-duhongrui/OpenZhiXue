from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient


class MongoDB:
    client: AsyncIOMotorClient = None
    sync_client: MongoClient = None
    database = None
    
    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.database = cls.client[settings.MONGODB_DB_NAME]
        cls.sync_client = MongoClient(settings.MONGODB_URL)
    
    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
        if cls.sync_client:
            cls.sync_client.close()
    
    @classmethod
    def get_database(cls):
        return cls.database
    
    @classmethod
    def get_collection(cls, name: str):
        return cls.database[name]


async def get_mongodb():
    return MongoDB.get_database()


async def init_mongodb():
    await MongoDB.connect()


async def close_mongodb():
    await MongoDB.close()
