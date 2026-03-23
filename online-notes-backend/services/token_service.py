
from authx import AuthX, AuthXConfig, RequestToken
from db.models import TokenModel
from sqlalchemy import select, delete
from datetime import timedelta, datetime, UTC
from config import settings

config = AuthXConfig()
config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
config.JWT_REFRESH_COOKIE_NAME = "refresh_token"
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ["cookies", "headers"]
config.JWT_CSRF_IN_COOKIES = False

security = AuthX(config=config)

class TokenService:
    async def generate_tokens(self, *, user_id: int):
        user_id_str = str(user_id)
        access_token = security.create_access_token(uid=user_id_str)
        refresh_token = security.create_refresh_token(uid=user_id_str, expiry=datetime.now(UTC)+timedelta(days=30))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def save_token(self, *, user_id: int, refresh_token: str, session):
        query = select(TokenModel).where(TokenModel.user_id==user_id)
        candidate = await session.execute(query)
        token_data = candidate.scalars().first()
        if token_data:
            token_data.refresh_token = refresh_token
            session.add(token_data)
            return await session.commit()
        token = TokenModel(
            user_id=user_id,
            refresh_token=refresh_token
        )
        session.add(token)
        await session.commit()
        return token
    
    async def remove_token(self, *, refresh_token: str, session):
        query = delete(TokenModel).where(TokenModel.refresh_token == refresh_token)
        candidate = await session.execute(query)
        await session.commit()
        return candidate
    
    async def validate_refresh_token(self, *, token: str):
        user_data = security.verify_token(RequestToken(token=token, type="refresh", location="cookies"), verify_csrf=False)
        return user_data
    
    async def validate_access_token(self, *, token: str):
        user_data = security.verify_token(RequestToken(token=token, type="access", location="headers"), verify_csrf=False)
        return user_data
    
    async def find_token(self, *, refresh_token: str, session):
        query = select(TokenModel).where(TokenModel.refresh_token == refresh_token)
        candidate = await session.execute(query)
        token_data = candidate.scalars().first()
        return token_data


token_service = TokenService()