from __future__ import annotations

from datetime import datetime
from ipaddress import IPv4Interface, IPv4Address
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, Extra
from pydantic.fields import ModelField

from myresearch.consts import RolesType
from myresearch.db.base import BaseFields, Document
from myresearch.db.mailcode import MailCodeFields
from myresearch.db.report import ReportFields
from myresearch.db.route import RouteFields
from myresearch.db.user import UserFields
from myresearch.db.duel import DuelFields
from myresearch.db.fund import FundFields
from myresearch.utils import roles_to_list


class BaseDBM(BaseModel):
    misc_data: dict[Any, Any] = Field(default={})

    # db fields
    oid: Optional[ObjectId] = Field(alias=BaseFields.oid)
    int_id: Optional[int] = Field(alias=BaseFields.int_id)
    created: Optional[datetime] = Field(alias=BaseFields.created)

    class Config:
        extra = Extra.ignore
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.timestamp()
        }

    def to_json(self, **kwargs) -> str:
        kwargs["indent"] = 2
        kwargs["ensure_ascii"] = False
        return self.json(**kwargs)

    def to_dict(self, only_db_fields: bool = True, **kwargs) -> dict:
        data = self.dict(**kwargs)
        if only_db_fields is True:
            for f in self.__fields__.values():
                f: ModelField
                if f.alias not in data:
                    continue
                if f.has_alias is False:
                    del data[f.alias]
                    continue
        return data

    @classmethod
    def parse_document(cls, doc: Document) -> BaseDBM:
        """get only fields that has alias and exists in doc"""
        doc_to_parse = {}
        for f in cls.__fields__.values():
            f: ModelField
            if f.has_alias is False:
                continue
            if f.alias not in doc:
                continue
            doc_to_parse[f.alias] = doc[f.alias]
        return cls.parse_obj(doc_to_parse)

    def document(self) -> Document:
        doc = self.dict(by_alias=True, exclude_none=False, exclude_unset=False, exclude_defaults=False)
        for f in self.__fields__.values():
            f: ModelField
            if f.alias not in doc:
                continue
            if f.has_alias is False:
                del doc[f.alias]
                continue
            if doc[f.alias] is None:
                continue
            if f.outer_type_ in [IPv4Interface, IPv4Address]:
                doc[f.alias] = str(doc[f.alias])
            elif f.outer_type_ in [list[IPv4Interface], list[IPv4Address]]:
                doc[f.alias] = [str(ip) for ip in doc[f.alias]]
        return doc


class User(BaseDBM):
    # db fields
    tokens: list[str] = Field(alias=UserFields.tokens, default=[])
    roles: list[str] = Field(alias=UserFields.roles, default=[])
    mail: Optional[str] = Field(alias=UserFields.mail)
    fullname: Optional[str] = Field(alias=UserFields.fullname)
    company: Optional[str] = Field(alias=UserFields.company)
    division: Optional[str] = Field(alias=UserFields.division)
    coins: Optional[int] = Field(alias=UserFields.coins)
    donations: Optional[int] = Field(alias=UserFields.donations)
    # direct linked models
    # ...

    # indirect linked models
    mail_codes: list[MailCode] = Field(default=[])

    def compare_roles(self, needed_roles: RolesType) -> bool:
        needed_roles = roles_to_list(needed_roles)
        return bool(set(needed_roles) & set(self.roles))

class Fund(BaseDBM):
    # db fields
    name: Optional[str] = Field(alias=FundFields.name)
    desc: Optional[str] = Field(alias=FundFields.desc)
    link: Optional[str] = Field(alias=FundFields.link)
    categories: Optional[str] = Field(alias=FundFields.categories)

class Duel(BaseDBM):
    # db fields
    bet: Optional[int] = Field(alias=DuelFields.bet)
    user_id: Optional[int] = Field(alias=DuelFields.user_id)
    owner_id: Optional[int] = Field(alias=DuelFields.owner_id)
    is_finish: Optional[bool] = Field(alias=DuelFields.is_finish)
    referee_id: Optional[int] = Field(alias=DuelFields.referee_id)
    winner_id: Optional[int] = Field(alias=DuelFields.winner_id)

class Route(BaseDBM):
    # db fields
    longitude: Optional[float] = Field(alias=RouteFields.longitude)
    latitude: Optional[float] = Field(alias=RouteFields.latitude)
    desc: Optional[str] = Field(alias=RouteFields.desc)

class Report(BaseDBM):
    # db fields
    duel_id: Optional[str] = Field(alias=ReportFields.duel_id)
    desc: Optional[str] = Field(alias=ReportFields.desc)
    user_id: Optional[int] = Field(alias=ReportFields.user_id)
    fullname: Optional[str] = Field(alias=ReportFields.fullname)

class MailCode(BaseDBM):
    # db fields
    to_mail: str = Field(alias=MailCodeFields.to_mail)
    code: str = Field(alias=MailCodeFields.code)
    type: str = Field(alias=MailCodeFields.type)  # use MailCodeTypes
    to_user_oid: Optional[ObjectId] = Field(alias=MailCodeFields.to_user_oid)

    # direct linked models
    to_user: Optional[User] = Field(default=None)
