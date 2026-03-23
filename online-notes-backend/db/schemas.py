from pydantic import BaseModel, Field, EmailStr


class NoteAddSchema(BaseModel):
    title: str
    description: str

class NoteSchema(NoteAddSchema):
    id: int
    user_id: int

class UserRegistrationSchema(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=16)
    password: str = Field(min_length=8, max_length=32)

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserSchema(UserRegistrationSchema):
    id: int
    is_activated: bool
    activation_link: str
    notes: list