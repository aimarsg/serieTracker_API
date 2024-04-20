from sqlalchemy import Column, Integer, String, Boolean, Date, Float, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from database import Base


class SerieCatalogo(Base):
    __tablename__ = "SerieCatalogo"

    titulo = Column(String, primary_key=True)
    numTemps = Column(Integer)
    epTemp = Column(String)


class SerieUsuario(Base):
    __tablename__ = "SerieUsuario"

    titulo = Column(String)
    numTemps = Column(Integer)
    epTemp = Column(String)

    siguiendo = Column(Boolean)
    recordatorio = Column(String)
    epActual = Column(Integer)
    tempActual = Column(Integer)
    valoracion = Column(Float)

    usuarioAsociado = Column(String, ForeignKey("Usuario.username"))

    usuario = relationship("Usuario", back_populates="series")

    # Definir una clave primaria compuesta
    __table_args__ = (
        PrimaryKeyConstraint('titulo', 'usuarioAsociado'),
    )

class Usuario(Base):
    __tablename__ = "Usuario"

    username = Column(String, primary_key=True)
    hashed_password = Column(String)

    series = relationship("SerieUsuario", back_populates="usuario")

class Marcador(Base):
    __tablename__ = "Marcador"

    nombre = Column(String, primary_key=True)
    latitud = Column(Float)
    longitud = Column(Float)
    

