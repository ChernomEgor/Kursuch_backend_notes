from fastapi import APIRouter, Depends
from db.database import SessionDep
from db.schemas import NoteAddSchema
from services.note_service import note_service
from services.token_service import security
from authx import RequestToken

router = APIRouter(prefix="/note")

@router.get("/get_user_notes", dependencies=[Depends(security.get_token_from_request())])
async def get_user_notes(session: SessionDep, access_token: RequestToken = Depends()):
    notes = await note_service.get_notes(access_token=access_token.token, session=session)
    return notes

@router.post("/create_user_note", dependencies=[Depends(security.get_token_from_request())])
async def create_user_note(data: NoteAddSchema, session: SessionDep, access_token: RequestToken = Depends()):
    note = await note_service.create_note(title=data.title, description=data.description, access_token=access_token.token, session=session)
    return note


@router.delete("/delete_user_note/{id}", dependencies=[Depends(security.get_token_from_request())])
async def delete_user_note(id: int, session: SessionDep, access_token: RequestToken = Depends()):
    note = await note_service.delete_note(id=id, access_token=access_token.token, session=session)
    return note


@router.patch("/update_user_note/{id}", dependencies=[Depends(security.get_token_from_request())])
async def update_user_note(id: int, data: NoteAddSchema, session: SessionDep, access_token: RequestToken = Depends()):
    note = await note_service.update_note(id=id, title=data.title, description=data.description, access_token=access_token.token, session=session)
    return note
