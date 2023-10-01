import pymongo

from charity.db.base import BaseCollection, BaseFields


class RouteFields(BaseFields):
    longitude = "longitude"
    latitude = "latitude"
    desc = "desc"

class RouteCollection(BaseCollection):
    COLLECTION_NAME = "route"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(RouteFields.int_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )