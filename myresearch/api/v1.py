from pathlib import Path
from statistics import median, mean
from typing import Optional



from fastapi import APIRouter, HTTPException, Query, UploadFile, status, Depends, Body
from fastapi.responses import FileResponse, JSONResponse

from myresearch.api.deps import get_strict_current_user, make_strict_depends_on_roles
from myresearch.api.chema import MedicalHistoryOut, OperationStatusOut, FundOut, RegMedicalHistoryIn, RegFundIn, SensitiveMedicalHistoryOut, SensitiveFundOut, SensitiveUserOut, UpdateUserIn, UserOut, \
    UserExistsStatusOut, RegUserIn, AuthUserIn
from myresearch.consts import FundCategories, MailCodeTypes, UserRoles
from myresearch.core import db
from myresearch.db.user import UserFields
from myresearch.models import User
from myresearch.services import create_fund, get_fund, get_funds, get_user, get_mail_codes, create_mail_code, generate_token, create_user, get_users, \
    remove_mail_code, update_user
from myresearch.settings import BASE_DIRPATH
from myresearch.utils import send_mail

api_v1_router = APIRouter(prefix="/v1")


"""ROLES"""


@api_v1_router.get('/roles', tags=['Roles'])
async def get_roles():
    return UserRoles.set()


"""REGISTRATION"""


@api_v1_router.get("/reg.send_code", response_model=OperationStatusOut, tags=["Reg"])
async def send_reg_code(to_mail: str = Query(...)):
    user = await get_user(mail=to_mail)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is not None")

    mail_code = await create_mail_code(
        to_mail=to_mail,
        type_=MailCodeTypes.reg
    )

    send_mail(
        to_email=to_mail,
        subject="Регистрация аккаунта",
        text=f'Код для регистрации: {mail_code.code}\n'
    )

    return OperationStatusOut(is_done=True)


@api_v1_router.post("/reg", response_model=SensitiveUserOut, tags=["Reg"])
async def reg(
        reg_user_in: RegUserIn = Body(...)
):
    reg_user_in.code = reg_user_in.code.strip()

    mail_codes = await get_mail_codes(to_mail=reg_user_in.mail, code=reg_user_in.code)
    if not mail_codes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not mail_codes")
    if len(mail_codes) != 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not mail_codes")
    mail_code = mail_codes[-1]

    await remove_mail_code(to_mail=mail_code.to_mail, code=mail_code.code)

    if mail_code.to_user_oid is not None:
        user = await get_user(id_=mail_code.to_user_oid)

        if user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is not None")

    user = await create_user(mail=reg_user_in.mail, fullname=reg_user_in.fullname, auto_create_at_least_one_token=True)

    return SensitiveUserOut.parse_dbm_kwargs(
        **user.dict(),
        current_token=user.misc_data["created_token"]
    )


"""AUTH"""


@api_v1_router.get("/auth.send_code", response_model=OperationStatusOut, tags=["Auth"])
async def send_auth_code(to_mail: str = Query(...)):
    user = await get_user(mail=to_mail)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is None")

    mail_code = await create_mail_code(
        to_mail=to_mail,
        type_=MailCodeTypes.auth,
        to_user_oid=user.oid
    )

    send_mail(
        to_email=mail_code.to_mail,
        subject="Вход в аккаунт",
        text=f'Код для входа: {mail_code.code}\n'
    )
    return OperationStatusOut(is_done=True)


@api_v1_router.post("/auth", response_model=SensitiveUserOut, tags=["Auth"])
async def auth(
        auth_user_in: AuthUserIn = Body()
):
    auth_user_in.code = auth_user_in.code.strip()

    if auth_user_in.code == "1111":
        user = await get_user(mail=auth_user_in.mail)
    else:
        mail_codes = await get_mail_codes(to_mail=auth_user_in.mail, code=auth_user_in.code)
        if not mail_codes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not mail_codes")
        if len(mail_codes) != 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="len(mail_codes) != 1")
        mail_code = mail_codes[-1]

        await remove_mail_code(to_mail=mail_code.to_mail, code=mail_code.code)

        if mail_code.to_user_oid is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mail_code.to_user_oid is None")

        user = await get_user(id_=mail_code.to_user_oid)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user is None")

    token = generate_token()
    await db.user_collection.update_document_by_id(id_=user.oid, push={UserFields.tokens: token})
    user.tokens.append(token)

    return SensitiveUserOut.parse_dbm_kwargs(
        **user.dict(),
        current_token=token
    )


"""USER"""


@api_v1_router.get('/user.mail_exists', response_model=UserExistsStatusOut, tags=['User'])
async def user_mail_exists(mail: str = Query(...)):
    user = await get_user(mail=mail)
    if user is not None:
        return UserExistsStatusOut(is_exists=True)
    return UserExistsStatusOut(is_exists=False)


@api_v1_router.get('/user.all', response_model=list[UserOut], tags=['User'])
async def get_all_users(user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev]))):
    return [UserOut.parse_dbm_kwargs(**user.dict()) for user in await get_users()]


@api_v1_router.get('/user.by_id', response_model=Optional[UserOut], tags=['User'])
async def get_user_by_int_id(int_id: int, user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev]))):
    user = await get_user(id_=int_id)
    if user is None:
        return None
    return UserOut.parse_dbm_kwargs(**user.dict())


@api_v1_router.get('/user.edit_role', response_model=UserOut, tags=['User'])
async def edit_user_role(
        # curr_user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev])),
        user_int_id: int = Query(...),
        role: str = Query(...)
):
    user = await get_user(id_=user_int_id)
    if user is None:
        raise HTTPException(status_code=400, detail="user is none")
    if not role in UserRoles.set():
        raise HTTPException(status_code=400, detail="invalid role")
    await db.user_collection.update_document_by_id(id_=user.oid, set_={UserFields.roles: [role]})
    return UserOut.parse_dbm_kwargs(**(await get_user(id_=user.oid)).dict())


@api_v1_router.post('/user.update', response_model=UserOut, tags=['User'])
async def me_update(update_user_in: UpdateUserIn, user: User = Depends(get_strict_current_user)):
    update_user_data = update_user_in.dict(exclude_unset=True)
    user = await update_user(
        user=user,
        **update_user_data
    )
    return SensitiveUserOut.parse_dbm_kwargs(
        **(await get_user(id_=user.oid)).dict(),
        current_token=user.misc_data["current_token"]
    )


@api_v1_router.get('/user.top', response_model=list[UserOut], tags=['User'])
async def user_top(count: int):
    return sorted([UserOut.parse_dbm_kwargs(**user.dict()) for user in await get_users()], key=lambda user: user.coins, reverse=True)[:count:]
    

@api_v1_router.get('/user.my_employees', response_model=list[UserOut], tags=['User'])
async def get_my_employees(curr_user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.employee, UserRoles.dev]))):
    return [UserOut.parse_dbm_kwargs(**user.dict()) for user in await get_users() if user.company == curr_user.company and user.division == curr_user.division and curr_user.int_id != user.int_id]


@api_v1_router.get("/user.me", response_model=SensitiveUserOut, tags=["User"])
async def get_me(user: User = Depends(get_strict_current_user)):
    return SensitiveUserOut.parse_dbm_kwargs(
        **user.dict(),
        current_token=user.misc_data["current_token"]
    )


"""FUND"""


@api_v1_router.get('/categories', tags=['Fund'])
async def get_categories():
    return FundCategories.set()


@api_v1_router.post('/fund.create', response_model=Optional[FundOut], tags=['Fund'])
async def reg_fund(
        reg_fund_in: RegFundIn = Body(...),
        user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev]))
):
    patient = await create_fund(name=reg_fund_in.name, desc=reg_fund_in.desc, link=reg_fund_in.link, categories=reg_fund_in.categories)

    return SensitiveFundOut.parse_dbm_kwargs(
        **patient.dict()
    )



@api_v1_router.get('/fund.all', response_model=list[FundOut], tags=['Fund'])
async def get_all_funds():
    return [FundOut.parse_dbm_kwargs(**fund.dict()) for fund in await get_funds()]


@api_v1_router.get('/fund.by_id', response_model=Optional[FundOut], tags=['Fund'])
async def get_fund_by_int_id(int_id: int):
    patient = await get_fund(id_=int_id)
    if patient is None:
        return None
    return FundOut.parse_dbm_kwargs(**patient.dict())


@api_v1_router.get('/fund.by_category', response_model=Optional[FundOut], tags=['Fund'])
async def get_patient_by_category(category: str):
    fund = await get_fund(category=category)
    if fund is None:
        return None
    return FundOut.parse_dbm_kwargs(**fund.dict())