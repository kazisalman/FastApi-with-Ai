from pydantic import BaseModel


class CreateUser(BaseModel):
    name: str
    email: str
    age: int | None = None


class UpdateUser(BaseModel):
    name: str | None = None
    email: str | None = None
    age: int | None = None
