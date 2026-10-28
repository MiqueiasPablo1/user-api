
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCriacao(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr


class UsuarioAtualizacao(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
