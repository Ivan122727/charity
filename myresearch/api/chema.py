from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from bson import ObjectId
from pydantic import BaseModel, Extra


class BaseSchema(BaseModel):
    class Config:
        extra = Extra.ignore
        arbitrary_types_allowed = True
        allow_population_by_field_name = True


class BaseSchemaOut(BaseSchema):
    misc: dict[str, Any] = {}


class BaseOutDBMSchema(BaseSchemaOut):
    oid: str
    int_id: int
    created: datetime

    @classmethod
    def parse_dbm_kwargs(
            cls,
            **kwargs
    ):
        res = {}
        for k, v in kwargs.items():
            if isinstance(v, ObjectId):
                v = str(v)
            res[k] = v
        return cls(**res)


class BaseSchemaIn(BaseSchema):
    pass


class UserOut(BaseOutDBMSchema):
    roles: list[str] = []
    mail: Optional[str]
    fullname: Optional[str]
    company: Optional[str]
    division: Optional[str]
    coins: Optional[int]
    donations: Optional[int]



class FundOut(BaseOutDBMSchema):
    name: Optional[str]
    desc: Optional[str]
    link: Optional[str]
    categories: Optional[str]

class DuelOut(BaseOutDBMSchema):
    bet: Optional[int]
    user_id: Optional[int]
    owner_id: Optional[int]
    referee_id: Optional[int]
    is_finish: Optional[bool]
    winner_id: Optional[int]

class ReportOut(BaseOutDBMSchema):
    user_id: Optional[int]
    desc: Optional[str]
    duel_id: Optional[int]
    fullname: Optional[str]

class RouteOut(BaseOutDBMSchema):
    longitude: Optional[float]
    latitude: Optional[float]
    desc: Optional[str]

class SensitiveUserOut(UserOut):
    tokens: list[str]
    current_token: str

class SensitiveFundOut(FundOut):
    ...

class SensitiveReportOut(ReportOut):
    ...

class SensitiveDuelOut(DuelOut):
    ...

class SensitiveRouteOut(RouteOut):
    ...


class OperationStatusOut(BaseSchemaOut):
    is_done: bool


class ExistsStatusOut(BaseSchemaOut):
    is_exists: bool


class UserExistsStatusOut(BaseSchemaOut):
    is_exists: bool


class RegUserIn(BaseSchemaIn):
    mail: str
    fullname: str
    code: str

class RegFundIn(BaseSchemaIn):
    name: str
    desc: str
    link: str
    categories: str

class RegDuelIn(BaseSchemaIn):
    owner_id: int
    bet: int

class RegRouteIn(BaseSchemaIn):
    longitude: float
    latitude: float
    desc: str

class EnterMemberDuelIn(BaseSchemaIn):
    user_id: int
    duel_id: int

class EnterRefereeDuelIn(BaseSchemaIn):
    referee_id: int
    duel_id: int

class SetResultDuelIn(BaseSchemaIn):
    referee_id: int
    duel_id: int
    winner_id: int
    is_finish: bool

class ReportDuelIn(BaseSchemaIn):
    duel_id: int
    desc: str
    user_id: int

class EditFundIn(RegFundIn):
    fund_id: int

class RegMedicalHistoryIn(BaseSchemaIn):
    patient_id: int
    result: str
    filepath: str
    user_id: int

class AuthUserIn(BaseSchemaIn):
    mail: str
    code: str

class UpdateUserIn(BaseSchemaIn):
    company: str
    division: str