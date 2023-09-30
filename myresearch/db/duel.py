import pymongo

from myresearch.db.base import BaseCollection, BaseFields


class DuelFields(BaseFields):
    bet = "bet"
    user_id = "user_id"
    owner_id = "owner_id"
    is_finish = "is_finish"
    referee_id = "referee_id"
    winner_id = "winner_id"

class DuelCollection(BaseCollection):
    COLLECTION_NAME = "duel"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(DuelFields.int_id, pymongo.ASCENDING), (DuelFields.owner_id, pymongo.ASCENDING), 
             (DuelFields.user_id, pymongo.ASCENDING), (DuelFields.referee_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )
