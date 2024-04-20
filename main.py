from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas import FirebaseClientToken, SeriesUsuarioList
from models import Usuario
import crud_operations as crud
import schemas
import models
from OAuthUtils import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user
from database import SessionLocal, engine
from pathlib import Path
import os

import firebase_admin
from firebase_admin import credentials, messaging

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# INICIALIZAR FIREBASE
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


# Directorio donde se guardarán las imágenes
IMAGES_DIRECTORY = "imagenes"

# Ruta completa al directorio de imágenes
FULL_IMAGES_DIRECTORY = Path(__file__).resolve().parent / IMAGES_DIRECTORY


########### Rutas para autenticacion y manejo de usuarios ############

# Ruta para obtener un usuario por su nombre de usuario
@app.get("/users/misDatos/", response_model=schemas.Usuario)
def get_user(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # db_user = crud.get_user(db, usuario.username)
    if usuario is None:
        raise HTTPException(status_code=404, detail="User not found")
    return usuario

@app.post("/users/subirFoto/")
async def subir_foto(usuario: Usuario = Depends(get_current_user), profile_pic: UploadFile | None = None):
    # Si se proporciona una imagen, procesarla y guardarla
    if profile_pic:
        image_bytes = profile_pic.file.read()
        
        # Verificar si la carpeta de imágenes existe, si no, crearla
        if not FULL_IMAGES_DIRECTORY.exists():
            FULL_IMAGES_DIRECTORY.mkdir()
        
        # Generar un nombre de archivo único para evitar conflictos
        image_filename = usuario.username
        image_path = FULL_IMAGES_DIRECTORY / image_filename
        
        # Escribir los bytes de la imagen en el archivo en el servidor
        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)
            print(f'imagen guardada: {image_path}')


@app.get("/users/obtenerFoto/")
async def obtener_foto(usuario: Usuario = Depends(get_current_user)):
    # Verificar si el usuario tiene una imagen asociada
    image_filename = f"{usuario.username}"  # Asumiendo que las imágenes están en formato JPG
    image_path = FULL_IMAGES_DIRECTORY / image_filename
    
    if image_path.exists():
        # Retornar la imagen como una respuesta de archivo
        return FileResponse(path=image_path)
    else:
        # Si la imagen no existe, devolver un error 404
        raise HTTPException(status_code=404, detail="La imagen solicitada no existe.")


# Ruta para crear un usuario
@app.post("/users/", response_model=schemas.Usuario)
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


# Ruta para obtener un token de acceso
@app.post("/token/", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


########### Rutas para acceder a los datos de las series ############


# Ruta para obtener todas las series del catálogo
@app.get("/series_catalogo/", response_model=list[schemas.SerieCatalogo])
def get_series_catalogo(db: Session = Depends(get_db)):
    return crud.get_series_catalogo(db)


# Ruta para crear una serie en el catálogo
@app.post("/series_catalogo/", response_model=schemas.SerieCatalogo)
def create_serie_catalogo(serieCatalogo: schemas.SerieCatalogoCreate, db: Session = Depends(get_db)):
    enviar_mensaje_a_todos("¡Hora de ver una nueva serie!", f"¡Nueva serie en el catálogo! {serieCatalogo.titulo}")
    return crud.create_serie_catalogo(db, serieCatalogo)


# Ruta para obtener todas las series de un usuario
@app.get("/users/misSeries/", response_model=list[schemas.SerieUsuarioBase])
def get_series_usuario(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # db_user = crud.get_user(db, username)
    if usuario is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_series_usuario(db, usuario.username)


# Ruta para crear una serie para un usuario
@app.post("/users/misSeries/", response_model=schemas.SerieUsuario)
def create_serie_usuario(serieUsuario: schemas.SerieUsuarioCreate, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # db_user = crud.get_user(db, username)
    if usuario is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_serie_usuario(db, serieUsuario, usuario.username)


# Ruta para actualizar una serie de un usuario
@app.put("/users/misSeries/{titulo}/", response_model=schemas.SerieUsuario)
def update_serie_usuario(titulo: str, serie_usuario_update: schemas.SerieUsuarioCreate,
                         usuario: Usuario = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    db_serie = crud.update_serie_usuario(db, titulo=titulo, usuario=usuario.username, serie_usuario_update=serie_usuario_update)
    if db_serie is None:
        crud.create_serie_usuario(db, serie_usuario_update, usuario)
        # raise HTTPException(status_code=404, detail="Serie usuario no encontrada")
    return db_serie


# Ruta para borrar una serie de un usuario
@app.delete("/series/misSeries/{titulo}/", response_model=schemas.SerieUsuario)
def delete_serie_usuario(titulo: str,
                         usuario: Usuario = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    db_serie = crud.get_serie_usuario_by_titulo_and_usuario(db, titulo=titulo, usuario=usuario.username)
    if db_serie is None:
        raise HTTPException(status_code=404, detail="Serie usuario no encontrada")
    db.delete(db_serie)
    db.commit()
    return db_serie


# Ruta para sincronizar las series de un usuario
@app.post("/users/misSeries/sincronizar/")
def sincronizar_series_usuario(series: SeriesUsuarioList, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # Eliminar las series guardadas en la bd del servidor
    crud.delete_series_usuario(db, usuario.username)
    #print(series)
    # Guardar la lista de series recibidas en el servidor
    for serie in series.seriesUsuario:
        crud.create_serie_usuario(db, serie, usuario.username)

    return {"success": True, "message": "Series sincronizadas correctamente"}


########### Rutas para los marcadores ############

# Ruta para rear un marcador
@app.post("/marcadores/", response_model=schemas.Marcador)
def create_marcador(marcador: schemas.MarcadorCreate, db: Session = Depends(get_db)):
    return crud.create_marcador(db, marcador)

# Ruta para obtener todos los marcadores
@app.get("/marcadores/", response_model=list[schemas.Marcador])
def get_marcadores(db: Session = Depends(get_db)):
    return crud.get_marcadores(db)


########### Rutas para notificaciones ############

# Método para suscribir un dispositivo al recibir un token de Firebase
@app.post("/suscribir_dispositivo/")
async def suscribir_dispositivo(token: FirebaseClientToken, usuario: Usuario = Depends(get_current_user)):
    #print(f"Token recibido: {token}")
    # Suscribir el dispositivo al tema "notificaciones"
    try:
        response = messaging.subscribe_to_topic([token.fcm_client_token], "notificaciones")
        #print(f"Dispositivo suscrito correctamente: {response}")
        return {"success": True, "message": f"Dispositivo suscrito correctamente: {response}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al suscribir el dispositivo: {e}")

# Método para enviar un mensaje a todos los dispositivos suscritos
@app.post("/enviar_mensaje/")
async def enviar_mensaje(titulo: str, mensaje: str):
    response = enviar_mensaje_a_todos(titulo, mensaje)
    return {"success": True, "message": f"Mensaje enviado correctamente: {response}"}


def enviar_mensaje_a_todos(titulo: str, mensaje: str):
    topic = "notificaciones"  # El mismo tema al que están suscritos los dispositivos
    
    # Crear el mensaje
    message = messaging.Message(
        notification=messaging.Notification(
            title=titulo,
            body=mensaje,
        ),
        topic=topic,
    )
    
    # Enviar el mensaje
    response = messaging.send(message)
    return response
    
