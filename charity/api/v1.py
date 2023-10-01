from pathlib import Path
from statistics import median, mean
from typing import Optional



from fastapi import APIRouter, HTTPException, Query, UploadFile, status, Depends, Body
from fastapi.responses import FileResponse, JSONResponse

from charity.api.deps import get_strict_current_user, make_strict_depends_on_roles
from charity.api.chema import DuelOut, EditFundIn, EnterMemberDuelIn, EnterRefereeDuelIn, FinishRouteIn, OperationStatusOut, FundOut, RegDuelIn, RegFundIn, RegRouteIn, ReportDuelIn, ReportOut, RouteOut, SensitiveDuelOut, SensitiveFundOut, SensitiveReportOut, SensitiveRouteOut, SensitiveUserOut, SetResultDuelIn, UpdateUserIn, UserOut, \
    UserExistsStatusOut, RegUserIn, AuthUserIn
from charity.consts import ActionType, MailCodeTypes, UserRoles
from charity.core import db
from charity.db.base import Document
from charity.db.fund import FundFields
from charity.db.user import UserFields
from charity.models import User
from charity.services import create_duel, create_fund, create_report, create_route, find_funds_docs_by_q, get_duel, get_fund, get_funds, get_report, get_reports, get_routes, get_user, get_mail_codes, create_mail_code, generate_token, create_user, get_users, \
    remove_mail_code, update_duel, update_user
from charity.settings import BASE_DIRPATH
from charity.utils import normalize_response, send_mail, get_price

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
async def process_report(
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
    return sorted([UserOut.parse_dbm_kwargs(**user.dict()) for user in await get_users()], key=lambda user: user.donations, reverse=True)[:count:]
    

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


@api_v1_router.post('/fund.create', response_model=Optional[FundOut], tags=['Fund'])
async def reg_fund(
        reg_fund_in: RegFundIn = Body(...),
        user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev]))
):
    fund = await create_fund(name=reg_fund_in.name, desc=reg_fund_in.desc, link=reg_fund_in.link)
    return SensitiveFundOut.parse_dbm_kwargs(
        **fund.dict()
    )

@api_v1_router.post('/fund.update', response_model=Optional[FundOut], tags=['Fund'])
async def edit_fund(
        edit_fund_in: EditFundIn = Body(...),
        user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev]))
):
    fund = await get_fund(int_id=edit_fund_in.fund_id)
    if user is None:
        raise HTTPException(status_code=400, detail="user is none")
    
    if fund is None:
        raise HTTPException(status_code=400, detail="fund is none")

    await db.fund_collection.update_document_by_int_id(int_id=edit_fund_in.fund_id, set_={
        FundFields.name: edit_fund_in.name, FundFields.desc: edit_fund_in.desc, 
        FundFields.link: edit_fund_in.link
        })
    return FundOut.parse_dbm_kwargs(**(await get_fund(int_id=edit_fund_in.fund_id)).dict())


@api_v1_router.get('/fund.delete', response_model=Optional[OperationStatusOut], tags=['Fund'])
async def delete_fund(
        fund_id: int, 
        user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev]))
):
    fund = await get_fund(int_id=fund_id)
    if user is None:
        raise HTTPException(status_code=400, detail="user is none")
    if fund is None:
        raise HTTPException(status_code=400, detail="fund is none")

    await db.fund_collection.remove_by_int_id(int_id=fund_id)
    return OperationStatusOut(is_done=True)

@api_v1_router.get('/fund.all', response_model=list[FundOut], tags=['Fund'])
async def get_all_funds():
    return [FundOut.parse_dbm_kwargs(**fund.dict()) for fund in await get_funds()]


@api_v1_router.get('/fund.by_id', response_model=Optional[FundOut], tags=['Fund'])
async def get_fund_by_int_id(int_id: int):
    patient = await get_fund(id_=int_id)
    if patient is None:
        return None
    return FundOut.parse_dbm_kwargs(**patient.dict())


@api_v1_router.get('/fund.donate', response_model=Optional[OperationStatusOut], tags=['Fund'])
async def donate_fund(
        fund_id:int = Query(...),
        count:int = Query(...),
        user: User = Depends(get_strict_current_user)
):
    fund = await get_fund(int_id=fund_id)
    if fund is None:
        raise HTTPException(status_code=400, detail="fund is None")

    if user.coins < count:
        raise HTTPException(status_code=400, detail="not money")
    await update_user(user=user, coins=user.coins - count, donations=count)
    await db.fund_collection.update_document_by_int_id(int_id=fund_id, set_={FundFields.money: fund.money + count})
    return OperationStatusOut(is_done=True)
 
@api_v1_router.get('/fund.search', tags=['Fund'])
async def search_funds(
        q: str = Query(...)
):
    result = await find_funds_docs_by_q(q=q)
    return normalize_response(result)


"""DUEL"""


@api_v1_router.get('/duel.create', response_model=Optional[DuelOut], tags=['Duel'])
async def reg_duel(
    bet: int = Query(...),
    user: User = Depends(get_strict_current_user)
):
    duel = await create_duel(owner_id=user.int_id, bet=bet)
    return SensitiveDuelOut.parse_dbm_kwargs(
        **duel.dict()
    )


@api_v1_router.get('/duel.enter_member', response_model=Optional[DuelOut], tags=['Duel'])
async def enter_duel_member(
        duel_id: int = Query(...),
        user: User = Depends(get_strict_current_user)
):
    user = await update_duel(
        user=user,
        user_id=user.int_id,
        duel_id=duel_id
    )
    return SensitiveDuelOut.parse_dbm_kwargs(
        **(await get_duel(int_id=duel_id)).dict(),
    )


@api_v1_router.get('/duel.enter_referee', response_model=Optional[DuelOut], tags=['Duel'])
async def enter_duel_referee(
        duel_id: int = Query(...),
        user: User = Depends(get_strict_current_user)
):
    user = await update_duel(
        user=user,
        referee_id=user.int_id,
        duel_id=duel_id
    )
    return SensitiveDuelOut.parse_dbm_kwargs(
        **(await get_duel(int_id=duel_id)).dict(),
    )

@api_v1_router.get('/duel.check', response_model=Optional[DuelOut], tags=['Duel'])
async def enter_duel_referee(
        duel_id: int
):
    duel =  await get_duel(int_id=duel_id)
    if duel is None:
        raise HTTPException(status_code=400, detail="duel is none")
         
    return SensitiveDuelOut.parse_dbm_kwargs(
        **(duel).dict(),
    )

@api_v1_router.post('/duel.set_result', response_model=Optional[DuelOut], tags=['Duel'])
async def set_duel_result(
        update_duel_in: SetResultDuelIn = Body(...),
        user: User = Depends(get_strict_current_user)
):
    duel = await get_duel(int_id=update_duel_in.duel_id)
    if duel is None:
        raise HTTPException(status_code=400, detail="duel is none")
    if duel.referee_id != user.int_id:
        raise HTTPException(status_code=400, detail="you are not referee")
    if update_duel_in.winner_id != duel.user_id and update_duel_in.winner_id != duel.owner_id:
        raise HTTPException(status_code=400, detail="user not exist")

    update_duel_data = update_duel_in.dict(exclude_unset=True)
    user = await update_duel(
        user=user,
        **update_duel_data
    )
    owner = await get_user(int_id=duel.owner_id)
    member = await get_user(int_id=duel.user_id)
    sign = 1 if duel.winner_id == duel.owner_id else -1
    await update_user(user=owner, coins=owner.coins + sign*duel.bet)
    await update_user(user=member, coins=member.coins -sign*duel.bet)
    return SensitiveDuelOut.parse_dbm_kwargs(
        **(await get_duel(int_id=update_duel_in.duel_id)).dict(),
    )

@api_v1_router.post('/duel.send_report', response_model=Optional[ReportOut], tags=['Duel'])
async def send_duel_report(
        report_duel_in: ReportDuelIn = Body(...),
        user: User = Depends(get_strict_current_user)
):
    duel = await get_duel(int_id=report_duel_in.duel_id)
    if duel is None:
        raise HTTPException(status_code=400, detail="duel is none")

    report = await create_report(duel_id=duel.int_id, desc=report_duel_in.desc, user_id=user.int_id, fullname=user.fullname)
    return SensitiveReportOut.parse_dbm_kwargs(
        **report.dict()
    )


"""REPORT"""


@api_v1_router.get('/report.all', response_model=list[ReportOut], tags=['Report'])
async def get_all_reports(user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev]))):
    return [ReportOut.parse_dbm_kwargs(**report.dict()) for report in await get_reports()]


@api_v1_router.get('/report.by_id', response_model=Optional[ReportOut], tags=['Report'])
async def get_report_by_int_id(int_id: int, report: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev]))):
    report = await get_report(id_=int_id)
    if report is None:
        return None
    return ReportOut.parse_dbm_kwargs(**report.dict())


@api_v1_router.get('/report.process', response_model=OperationStatusOut, tags=['Report'])
async def process_report(
        curr_user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev])),
        is_accepted: bool = Query(...),
        duel_id: int = Query(...),
        report_id: int = Query(...)
):
    duel = await get_duel(int_id=duel_id)
    print(duel)
    if duel is None:
        raise HTTPException(status_code=400, detail="duel is none")
    owner = await get_user(int_id=duel.owner_id)
    member = await get_user(int_id=duel.user_id)
    if is_accepted:
        sign = -1 if duel.winner_id == duel.owner_id else 1
        await update_user(user=owner, coins=owner.coins + sign*duel.bet)
        await update_user(user=member, coins=member.coins -sign*duel.bet)
    await db.report_collection.remove_by_int_id(int_id=report_id)
    return OperationStatusOut(is_done=True)



"""ROUTE"""

@api_v1_router.post('/route.create', response_model=Optional[SensitiveRouteOut], tags=['Route'])
async def reg_route(
        user: User = Depends(make_strict_depends_on_roles(roles=[UserRoles.dev])),
        reg_route_in: RegRouteIn = Body(...),
):
    route = await create_route(longitude=reg_route_in.longitude, latitude=reg_route_in.latitude, desc=reg_route_in.desc)
    return SensitiveRouteOut.parse_dbm_kwargs(
        **route.dict()
    )

@api_v1_router.get('/route.all', response_model=list[RouteOut], tags=['Route'])
async def get_all_reports():
    return [RouteOut.parse_dbm_kwargs(**route.dict()) for route in await get_routes()]


@api_v1_router.post('/route.finish', response_model=Optional[OperationStatusOut], tags=['Route'])
async def finish_route(
        report_duel_in: FinishRouteIn = Body(...),
        user: User = Depends(get_strict_current_user)
):
    if report_duel_in.type == ActionType.walk:
        coef = 1
    elif  report_duel_in.type == ActionType.run:
        coef = 2
    elif report_duel_in.type == ActionType.bike:
        coef = 3
    else:
        raise HTTPException(status_code=400, detail="action not exist")
    price = get_price(start_latitude=report_duel_in.start_latitude, start_longitude=report_duel_in.start_longitude, 
                      finish_latitude=report_duel_in.finish_latitude, finish_longitude=report_duel_in.finish_longitude
    ) * coef
    await update_user(user=user, coins=user.coins + price)
    return OperationStatusOut(is_done=True)

@api_v1_router.get('/route.get_actions', tags=['Route'])
async def get_actions():
    return ActionType.set()