import pymongo

from myresearch.db.base import BaseCollection, BaseFields


class RouteFields(BaseFields):
    price = "price"
    user_id = "user_id"
    type = "type"
    time_destroy = "time_destroy"

class RouteCollection(BaseCollection):
    COLLECTION_NAME = "route"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(RouteFields.int_id, pymongo.ASCENDING), (RouteFields.user_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )
