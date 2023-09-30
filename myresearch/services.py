import logging
import os
from random import randint
from typing import Union, Optional
from statistics import mean, median
import binascii

import pymongo
from bson import ObjectId

from myresearch.consts import UserRoles, RolesType
from myresearch.core import db
from myresearch.db.base import Id
from myresearch.db.mailcode import MailCodeFields
from myresearch.db.fund import FundFields
from myresearch.db.user import UserFields
from myresearch.db.duel import DuelFields
from myresearch.helpers import NotSet, is_set
from myresearch.models import Fund, User, MailCode, Duel
from myresearch.utils import roles_to_list
from myresearch.utils import send_mail

log = logging.getLogger()


"""TOKEN LOGIC"""


def generate_token() -> str:
    res = binascii.hexlify(os.urandom(20)).decode() + str(randint(10000, 1000000))
    return res[:128]

async def remove_token(*, client_id: Id, token: str):
    await db.user_collection.motor_collection.update_one(
        db.user_collection.create_id_filter(id_=client_id),
        {'$pull': {UserFields.tokens: token}}
    )


"""USER LOGIC"""

async def create_user(
        *,
        mail: Optional[str] = None,
        fullname: Optional[str] = None,
        company: Optional[str] = None,
        division: Optional[str] = None,
        tokens: Optional[list[str]] = None,
        auto_create_at_least_one_token: bool = True,
        roles: RolesType = None
):
    if roles is None:
        roles = [UserRoles.user]
    else:
        roles = roles_to_list(roles)

    created_token: Optional[str] = None
    if tokens is None:
        tokens = []
        if auto_create_at_least_one_token is True:
            created_token = generate_token()
            tokens.append(created_token)

    doc_to_insert = {
        UserFields.fullname: fullname,
        UserFields.mail: mail,
        UserFields.roles: roles,
        UserFields.tokens: tokens,
        UserFields.company: company,
        UserFields.division: division,
        UserFields.coins: 0,
        UserFields.donations: 0,

    }
    inserted_doc = await db.user_collection.insert_document(doc_to_insert)
    created_user = User.parse_document(inserted_doc)
    created_user.misc_data["created_token"] = created_token
    return created_user

async def get_user(
        *,
        id_: Optional[Id] = None,
        mail: Optional[str] = None,
        int_id: Optional[int] = None,
        token: Optional[str] = None,
) -> Optional[User]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.user_collection.create_id_filter(id_=id_))
    if int_id is not None:
        filter_[UserFields.int_id] = int_id
    if mail is not None:
        filter_[UserFields.mail] = mail
    if token is not None:
        filter_[UserFields.tokens] = {"$in": [token]}

    if not filter_:
        raise ValueError("not filter_")

    doc = await db.user_collection.find_document(filter_=filter_)
    if doc is None:
        return None
    return User.parse_document(doc)

async def get_users(*, roles: Optional[list[str]] = None) -> list[User]:
    users = [User.parse_document(doc) async for doc in db.user_collection.create_cursor()]
    if roles is not None:
        users = [user for user in users if user.compare_roles(roles)]
    return users

async def update_user(
        *,
        user: Union[User, ObjectId],
        company: Union[NotSet, Optional[str]] = NotSet, 
        division: Union[NotSet, Optional[str]] = NotSet, 
) -> User:
    if isinstance(user, User):
        pass
    elif isinstance(user, ObjectId):
        user = await get_user(id_=user)
    else:
        raise TypeError("bad type for user")

    if user is None:
        raise ValueError("user is None")

    set_ = {}
    if is_set(company):
        set_[UserFields.company] = company
    if is_set(division):
        set_[UserFields.division] = division

    if set_:
        await db.user_collection.update_document_by_id(
            id_=user.oid,
            set_=set_
        )

    return user

"""FUND LOGIC"""

async def create_fund(
        *,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        link: Optional[str] = None,
        categories: Optional[str] = None,
):
    doc_to_insert = {
        FundFields.name: name,
        FundFields.desc: desc,
        FundFields.link: link,
        FundFields.categories: categories,
    }
    inserted_doc = await db.fund_collection.insert_document(doc_to_insert)
    created_fund = Fund.parse_document(inserted_doc)
    return created_fund

async def get_fund(
        *,
        id_: Optional[Id] = None,
        int_id: Optional[int] = None,
        category: Optional[str] = None,
) -> Optional[Fund]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.fund_collection.create_id_filter(id_=id_))
    if int_id is not None:
        filter_[FundFields.int_id] = int_id
    if category is not None:
        filter_[FundFields.categories] = category

    if not filter_:
        raise ValueError("not filter_")

    doc = await db.fund_collection.find_document(filter_=filter_)
    if doc is None:
        return None
    return Fund.parse_document(doc)

async def get_funds(*, roles: Optional[list[str]] = None) -> list[Fund]:
    funds = [Fund.parse_document(doc) async for doc in db.fund_collection.create_cursor()]
    if roles is not None:
        funds = [fund for fund in funds if funds.compare_roles(roles)]
    return funds


"""MAIL CODE LOGIC"""


async def remove_mail_code(
        *,
        id_: Optional[Id] = None,
        to_mail: Optional[str] = None,
        code: Optional[str] = None
):
    filter_ = {}
    if id_ is not None:
        filter_.update(db.mail_code_collection.create_id_filter(id_=id_))
    if to_mail is not None:
        filter_[MailCodeFields.to_mail] = to_mail
    if code is not None:
        filter_[MailCodeFields.code] = code

    if not filter_:
        raise ValueError("not filter_")

    await db.mail_code_collection.remove_document(
        filter_=filter_
    )


def _generate_mail_code() -> str:
    return str(randint(1, 9)) + str(randint(1, 9)) + str(randint(1, 9)) + str(randint(1, 9))


async def generate_unique_mail_code() -> str:
    mail_code = _generate_mail_code()
    while await db.mail_code_collection.document_exists(filter_={MailCodeFields.code: mail_code}):
        mail_code = _generate_mail_code()
    return mail_code


async def get_mail_codes(
        *,
        id_: Optional[Id] = None,
        to_mail: Optional[str] = None,
        code: Optional[str] = None,
        type_: Optional[str] = None,  # use MailCodeTypes
        to_user_oid: Union[NotSet, Optional[ObjectId]] = NotSet
) -> list[MailCode]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.mail_code_collection.create_id_filter(id_=id_))
    if to_mail is not None:
        filter_[MailCodeFields.to_mail] = to_mail
    if code is not None:
        filter_[MailCodeFields.code] = code
    if type_ is not None:
        filter_[MailCodeFields.type] = type_
    if is_set(to_user_oid):
        filter_[MailCodeFields.to_user_oid] = to_user_oid

    cursor = db.mail_code_collection.create_cursor(
        filter_=filter_,
        sort_=[(MailCodeFields.created, pymongo.DESCENDING)],
    )

    return [MailCode.parse_document(doc) async for doc in cursor]


async def create_mail_code(
        *,
        to_mail: str,
        code: str = None,
        type_: str,  # use MailCodeTypes
        to_user_oid: Optional[ObjectId] = None
) -> MailCode:
    to_user: Optional[User] = None
    if to_user_oid is not None:
        to_user = await get_user(id_=to_user_oid)
        if to_user is None:
            raise Exception("to_user is None")

    if code is None:
        code = await generate_unique_mail_code()

    doc_to_insert = {
        MailCodeFields.to_mail: to_mail,
        MailCodeFields.code: code,
        MailCodeFields.type: type_,
        MailCodeFields.to_user_oid: to_user_oid
    }
    inserted_doc = await db.mail_code_collection.insert_document(doc_to_insert)
    created_mail_code = MailCode.parse_document(inserted_doc)

    created_mail_code.to_user = to_user

    return created_mail_code
