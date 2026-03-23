from fastapi import HTTPException
from db.models import NoteModel
from sqlalchemy import select, delete
from .token_service import token_service
import datetime

class NoteService:
    async def get_notes(self, *, access_token: str, session):
        user_data = await token_service.validate_access_token(token=access_token)
        if (not user_data):
            HTTPException(status_code=401)

        query = select(NoteModel).where(NoteModel.user_id==int(user_data.sub))
        candidate = await session.execute(query)
        notes = candidate.scalars().all()

        return notes
    
    
    async def create_note(self, *, title: str, description: str, access_token: str, session):
        user_data = await token_service.validate_access_token(token=access_token)
        if (not user_data):
            HTTPException(status_code=401)

        new_note = NoteModel(
            user_id = int(user_data.sub),
            title=title,
            description=description
        )
        session.add(new_note)
        await session.commit()
        return new_note
    
    async def delete_note(self, *, id: int, access_token: str, session):
        user_data = await token_service.validate_access_token(token=access_token)
        if (not user_data):
            HTTPException(status_code=401)

        query = delete(NoteModel).where(NoteModel.user_id==int(user_data.sub)).where(NoteModel.id==id)
        candidate = await session.execute(query)
        await session.commit()
        return candidate
    
    async def update_note(self, *, id: int, title: str, description: str, access_token: str, session):
        user_data = await token_service.validate_access_token(token=access_token)
        if (not user_data):
            HTTPException(status_code=401)

        query = select(NoteModel).where(NoteModel.user_id==int(user_data.sub)).where(NoteModel.id==id)
        candidate = await session.execute(query)
        note = candidate.scalars().first()
        note.title = title
        note.description = description
        note.date = datetime.datetime.now()
        session.refresh(note)
        return await session.commit()


note_service = NoteService()