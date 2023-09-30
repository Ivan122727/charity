import pymongo

from myresearch.db.base import BaseCollection, BaseFields


class UserFields(BaseFields):
    fullname = "fullname"
    roles = "roles"
    tokens = "tokens"
    mail = "mail"
    company = "company"
    division = "division"
    coins = "coins"
    donations = "donations"

class UserCollection(BaseCollection):
    COLLECTION_NAME = "user"

    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(UserFields.int_id, pymongo.ASCENDING), (UserFields.mail, pymongo.ASCENDING)],
            unique=True, sparse=True
        )
