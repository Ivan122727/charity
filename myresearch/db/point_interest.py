import pymongo

from myresearch.db.base import BaseCollection, BaseFields


class PointInterestFields(BaseFields):
    longitude = "longitude"
    latitude = "latitude"
    desc = "desc"

class PointInterestCollection(BaseCollection):
    COLLECTION_NAME = "point_interest"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(PointInterestFields.int_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )
