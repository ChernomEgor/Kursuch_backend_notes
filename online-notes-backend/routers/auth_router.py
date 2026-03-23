from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import RedirectResponse
from db.schemas import UserRegistrationSchema, UserLoginSchema
from db.database import SessionDep
from services.user_service import user_service
from services.token_service import security
from config import settings

router = APIRouter(prefix="/auth")

@router.post("/registration")
async def registration(data: UserRegistrationSchema, session: SessionDep, res: Response):
    user_data = await user_service.registration(email=data.email, password=data.password, username=data.username, session=session)
    res.set_cookie("refresh_token", user_data["refresh_token"], max_age=30*24*60*60, httponly=True, secure=True, samesite="none", partitioned=True)
    return user_data


@router.post("/login")
async def login(data: UserLoginSchema, session: SessionDep, res: Response):
    user_data = await user_service.login(email=data.email, password=data.password, session=session)
    res.set_cookie("refresh_token", user_data["refresh_token"], max_age=30*24*60*60, httponly=True, secure=True, samesite="none", partitioned=True)
    return user_data


@router.get("/refresh", dependencies=[Depends(security.refresh_token_required)])
async def refresh(req: Request, res: Response, session: SessionDep):
    refresh_token = req.cookies["refresh_token"]
    
    user_data = await user_service.refresh(refresh_token=refresh_token, session=session)
    res.set_cookie("refresh_token", user_data["refresh_token"], max_age=30*24*60*60, httponly=True, secure=True, samesite="none", partitioned=True)
    return user_data


@router.post("/logout")
async def logout(req: Request, res: Response, session: SessionDep):
    refresh_token = req.cookies["refresh_token"]
    await user_service.logout(refresh_token=refresh_token, session=session)
    res.set_cookie("refresh_token", max_age=0, expires=0, secure=True, samesite="none", partitioned=True)
    return {"status_code": 200}


@router.get("/activate/{activation_link}")
async def activate(activation_link: str, session: SessionDep):
    activation_link = f"https://quickly-benevolent-moose.cloudpub.ru/auth/activate/{activation_link}"
    await user_service.activate(activation_link=activation_link, session=session)
    return RedirectResponse(url=settings.CLIENT_URL, status_code=302)