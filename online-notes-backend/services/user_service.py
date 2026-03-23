from fastapi import HTTPException
from db.models import UserModel
from sqlalchemy import select
from bcrypt import hashpw, gensalt, checkpw
from uuid import uuid4
from config import settings
from services.mail_service import send_mail
from .token_service import token_service

class UserService:
    async def registration(self, *, email: str, password: str, username: str, session):
        query = select(UserModel).where(UserModel.email==email)
        candidate = await session.execute(query)
        user = candidate.scalars().first()
        if user:
            raise HTTPException(status_code=401, detail="Пользователь с таким email уже существует.")

        password_bytes = password.encode('utf-8')
        hash_password = hashpw(password_bytes, gensalt()).decode('utf-8')
        activation_link = f"https://quickly-benevolent-moose.cloudpub.ru/auth/activate/{str(uuid4())}"
        await send_mail(send_to=email, activation_link=activation_link)

        new_user = UserModel(
            email = email,
            password = hash_password,
            username = username,
            activation_link = activation_link
        )
        session.add(new_user)
        await session.commit()

        tokens = await token_service.generate_tokens(user_id=new_user.id)
        await token_service.save_token(user_id=new_user.id, refresh_token=tokens["refresh_token"], session=session)

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "user" : {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "is_activated": new_user.is_activated
            }
        }
    
    async def activate(self, *, activation_link: str, session):
        query = select(UserModel).where(UserModel.activation_link==activation_link)
        candidate = await session.execute(query)
        user = candidate.scalars().first()
        if user == None:
            raise HTTPException(status_code=401, detail="Некорректная ссылка для активации.")
        user.is_activated = True
        session.refresh(user)
        return await session.commit()
    
    async def login(self, *, email: str, password: str, session):
        query = select(UserModel).where(UserModel.email==email)
        candidate = await session.execute(query)
        user = candidate.scalars().first()
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь с таким email не существует.")
        
        password_bytes = password.encode('utf-8')
        is_pass_equals = checkpw(password_bytes, user.password.encode('utf-8'))

        if not is_pass_equals:
            raise HTTPException(status_code=401, detail="Неверный пароль.")
        
        tokens = await token_service.generate_tokens(user_id=user.id)
        await token_service.save_token(user_id=user.id, refresh_token=tokens["refresh_token"], session=session)

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_activated": user.is_activated
            }
        }
    
    async def logout(self, *, refresh_token: str, session):
        token = await token_service.remove_token(refresh_token=refresh_token, session=session)
        return token
    
    async def refresh(self, *, refresh_token: str, session):
        if (not refresh_token):
            raise HTTPException(status_code=401)
        user_data = await token_service.validate_refresh_token(token=refresh_token)
        token_from_db = await token_service.find_token(refresh_token=refresh_token, session=session)

        if (not user_data or not token_from_db):
            HTTPException(status_code=401)

        query = select(UserModel).where(UserModel.id==int(user_data.sub))
        candidate = await session.execute(query)
        user = candidate.scalars().first()
        
        tokens = await token_service.generate_tokens(user_id=user.id)
        await token_service.save_token(user_id=user.id, refresh_token=tokens["refresh_token"], session=session)

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "user" : {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_activated": user.is_activated
            }
        }


user_service = UserService()