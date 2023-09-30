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

class MedicalHistoryOut(BaseOutDBMSchema):
    patient_id: Optional[int]
    result: Optional[str]
    filepath: Optional[str]
    user_id: Optional[int]


class SensitiveUserOut(UserOut):
    tokens: list[str]
    current_token: str

class SensitiveFundOut(FundOut):
    ...

class SensitiveMedicalHistoryOut(MedicalHistoryOut):
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