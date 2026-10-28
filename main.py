
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Usuario
from schemas import UsuarioAtualizacao, UsuarioCriacao, UsuarioResposta


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="User API", lifespan=lifespan)


@app.post(
    "/usuarios",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_usuario(dados: UsuarioCriacao, db: Session = Depends(get_db)):
    usuario_existente = db.scalar(
        select(Usuario).where(Usuario.email == str(dados.email))
    )

    if usuario_existente:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    usuario = Usuario(nome=dados.nome, email=str(dados.email))
    db.add(usuario)

    try:
        db.commit()
        db.refresh(usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    return usuario


@app.get("/usuarios", response_model=list[UsuarioResposta])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.scalars(select(Usuario).order_by(Usuario.id)).all()


@app.get("/usuarios/{usuario_id}", response_model=UsuarioResposta)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return usuario


@app.patch("/usuarios/{usuario_id}", response_model=UsuarioResposta)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioAtualizacao,
    db: Session = Depends(get_db),
):
    usuario = db.get(Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    alteracoes = dados.model_dump(exclude_unset=True)

    if not alteracoes or all(valor is None for valor in alteracoes.values()):
        raise HTTPException(status_code=400, detail="Nenhum dado válido enviado")

    for campo, valor in alteracoes.items():
        if valor is not None:
            setattr(usuario, campo, str(valor) if campo == "email" else valor)

    try:
        db.commit()
        db.refresh(usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    return usuario


@app.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(usuario)
    db.commit()
