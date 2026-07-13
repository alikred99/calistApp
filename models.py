from sqlalchemy import Column, String, Date, INTEGER, ForeignKey, Time
from databases import Base
from datetime import date
class Ejercicio(Base):
    __tablename__  = "ejercicios"

    id = Column(INTEGER, primary_key=True)
    nombre = Column(String, nullable=False)
    fecha = Column(Date, default=date.today)
    reps = Column(INTEGER, default=0)
    series = Column(INTEGER, default=0)
    sesion_id = Column(INTEGER, ForeignKey("sesiones.id"))

class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(INTEGER, primary_key=True)
    fecha = Column(Date, default=date.today)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time)

class Catalogo(Base):
    __tablename__ = "catalogo_ejercicios"

    id = Column(INTEGER, primary_key=True)
    nombre = Column(String, nullable=False)