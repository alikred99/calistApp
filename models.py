from sqlalchemy import Column, String, Date, INTEGER, ForeignKey, Time, Text
from databases import Base
from datetime import date
class Ejercicio(Base):
    __tablename__  = "ejercicios"

    id = Column(INTEGER, primary_key=True)
    nombre = Column(String, nullable=False)
    reps = Column(INTEGER, default=0)
    series = Column(INTEGER, default=0)
    sesion_id = Column(INTEGER, ForeignKey("sesiones.id"))

class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(INTEGER, primary_key=True)
    fecha = Column(Date, default=date.today)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time)
    rutina_id = Column(INTEGER, ForeignKey("rutinas.id"))

class Catalogo(Base):
    __tablename__ = "catalogo_ejercicios"

    id = Column(INTEGER, primary_key=True)
    nombre = Column(String, nullable=False)


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(INTEGER, primary_key=True)
    usuario = Column(String, nullable=False)
    contrasena = Column(Text, nullable=False)


class Rutina(Base):
    __tablename__ = "rutinas"
    id = Column(INTEGER, primary_key=True)
    nombre = Column(String, nullable=False)

class RutinaEjercicio(Base):
    __tablename__ = "rutina_ejercicio"

    id = Column(INTEGER, primary_key=True)
    orden = Column(INTEGER, nullable=False)
    reps = Column(INTEGER, nullable=False)
    series = Column(INTEGER, nullable=False)
    id_rutina = Column(INTEGER, ForeignKey("rutinas.id"))
    id_ejercicios = Column(INTEGER, ForeignKey("catalogo_ejercicios.id"))

