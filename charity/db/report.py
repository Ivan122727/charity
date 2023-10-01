import pymongo

from charity.db.base import BaseCollection, BaseFields


class ReportFields(BaseFields):
    duel_id = "duel_id"
    desc = "desc"
    user_id = "user_id"
    fullname = "fullname"

class ReportCollection(BaseCollection):
    COLLECTION_NAME = "report"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(ReportFields.int_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )
