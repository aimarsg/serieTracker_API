from sqlalchemy.orm import Session
import models
import schemas
from OAuthUtils import get_password_hash
from fastapi import FastAPI, Depends, HTTPException


def get_user(db: Session, username: str):
    return db.query(models.Usuario).filter(models.Usuario.username == username).first()


def create_user(db: Session, user: schemas.UsuarioCreate):
    usuario_existente = get_user(db=db, username=user.username)
    if usuario_existente:
        raise HTTPException(status_code=409, detail="El usuario ya existe")
    hashed_passwd = get_password_hash(user.hashed_password)
    db_user = models.Usuario(username=user.username, hashed_password=hashed_passwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_series_catalogo(db: Session):
    return db.query(models.SerieCatalogo).all()


def create_serie_catalogo(db: Session, serieCatalogo: schemas.SerieCatalogoCreate):
    db_serie_catalogo = models.SerieCatalogo(titulo= serieCatalogo.titulo, numTemps=serieCatalogo.numTemps, epTemp=serieCatalogo.epTemp)
    db.add(db_serie_catalogo)
    db.commit()
    db.refresh(db_serie_catalogo)
    return db_serie_catalogo


def get_series_usuario(db: Session, username: str):
    return db.query(models.SerieUsuario).filter(models.SerieUsuario.usuarioAsociado == username)


def get_serie_usuario_by_titulo_and_usuario(db: Session, titulo: str, usuario: str):
    return db.query(models.SerieUsuario).filter(models.SerieUsuario.titulo == titulo, models.SerieUsuario.usuarioAsociado == usuario).first()


def create_serie_usuario(db: Session, serieUsuario: schemas.SerieUsuarioCreate, usuario: str):
    db_serie = models.SerieUsuario(**serieUsuario.dict(), usuarioAsociado=usuario)
    db.add(db_serie)
    db.commit()
    db.refresh(db_serie)
    return db_serie


# function to update a serie
def update_serie_usuario(db: Session, titulo: str, usuario: str, serie_usuario_update: schemas.SerieUsuarioCreate):
    db_serie = db.query(models.SerieUsuario).filter(models.SerieUsuario.titulo == titulo, models.SerieUsuario.usuarioAsociado == usuario).first()
    if db_serie:
        for key, value in serie_usuario_update.dict().items():
            setattr(db_serie, key, value)
        db.commit()
        db.refresh(db_serie)
        return db_serie
    return None


# function to delete all series
def delete_series_usuario(db: Session, usuario: str):
    db_serie = db.query(models.SerieUsuario).filter(models.SerieUsuario.usuarioAsociado == usuario).all()
    for serie in db_serie:
        db.delete(serie)
    db.commit()
    #return db_serie


# function to delete a serie
def delete_serie_usuario(db: Session, serieUsuario: schemas.SerieUsuarioCreate, usuario: str):
    db_serie = models.SerieUsuario(**serieUsuario.dict())
    db.delete(db_serie)
    db.commit()
    return db_serie


# function to add a new marador
def create_marcador(db: Session, marcador: schemas.MarcadorCreate):
    db_marcador = models.Marcador(**marcador.dict())
    db.add(db_marcador)
    db.commit()
    db.refresh(db_marcador)
    return db_marcador


# function to get all marcadores
def get_marcadores(db: Session):
    return db.query(models.Marcador).all()
