import asyncio

from charity.cache_dir import CacheDir
from charity.db.db import DB
from charity.settings import Settings
from pymorphy2 import MorphAnalyzer

settings = Settings()
db = DB(mongo_uri=settings.mongo_uri, mongo_db_name=settings.mongo_db_name)
cache_dir = CacheDir(settings.cache_dirpath)
morpher = MorphAnalyzer(lang="ru")
