

from pydantic import BaseModel


class SerieBase(BaseModel):
    titulo: str
    numTemps: int
    epTemp: str


class SerieCatalogoCreate(SerieBase):
    pass


class SerieCatalogo(SerieBase):
    class Config:
        orm_mode = True


class SerieUsuarioBase(SerieBase):
    siguiendo: bool
    recordatorio: str
    epActual: int
    tempActual: int
    valoracion: float
    


class SerieUsuarioCreate(SerieUsuarioBase):
    pass


class SerieUsuario(SerieUsuarioBase):
    usuarioAsociado: str
    class Config:
        orm_mode = True


class UsuarioBase(BaseModel):
    username: str


class UsuarioCreate(UsuarioBase):
    hashed_password: str


class Usuario(UsuarioBase):
    series: list[SerieUsuario] = []

    class Config:
        orm_mode = True


# token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None

# marcador
class MarcadorBase(BaseModel):
    nombre: str
    latitud: float
    longitud: float

class MarcadorCreate(MarcadorBase):
    pass

class Marcador(MarcadorBase):
    class Config:
        orm_mode = True

class FirebaseClientToken(BaseModel):
    fcm_client_token: str

class SeriesUsuarioList(BaseModel):
    seriesUsuario: list[SerieUsuarioBase]
