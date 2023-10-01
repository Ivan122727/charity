import pymongo

from charity.db.base import BaseCollection, BaseFields


class FundFields(BaseFields):
    name = "name"
    desc = "desc"
    money = "money"
    link = "link"
    categories = "categories"

class FundCollection(BaseCollection):
    COLLECTION_NAME = "fund"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(FundFields.int_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )
