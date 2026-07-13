from fastapi import FastAPI, HTTPException
from models import Ejercicio, Sesion, Catalogo
from pydantic import BaseModel, Field, field_serializer
from databases import SessionLocal
from datetime import date, time, datetime
from typing import List
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class EjercicioBase(BaseModel):
    nombre: str
    reps: int = Field(gt=0)
    series: int = Field(gt=0)

class SesionBase(BaseModel):
    hora_inicio: time


class SesionUpdate(BaseModel):
    hora_fin: time
class EjercicioResponse(BaseModel):
    id: int
    nombre: str
    reps: int
    series: int
    fecha: date

    @field_serializer('fecha')
    def formatear_fecha(self, fecha: date) -> str:
        return fecha.strftime("%d/%m/%y")
    
    class Config:
        from_attributes = True



@app.get("/ejercicios",response_model=List[EjercicioResponse])
def listar_ejercicios():
    db = SessionLocal()
    try:
        ejercicios = db.query(Ejercicio).all()
        return ejercicios
    finally:
        db.close()



@app.get("/sesiones")
def listar_sesiones():
    db = SessionLocal()
    try:
        sesiones = db.query(Sesion).all()
        return sesiones
    finally:
        db.close()
    
@app.get("/sesiones/historial")
def listar_historial_sesiones():
    db = SessionLocal()
    try:
        sesiones = db.query(Sesion).all()
        resultado = []
        for sesion in sesiones:
            ejercicios_de_sesion = db.query(Ejercicio).filter(Ejercicio.sesion_id == sesion.id).all()
            inicio_completo = datetime.combine(sesion.fecha, sesion.hora_inicio)
            fin_completo = datetime.combine(sesion.fecha, sesion.hora_fin)
            duracion = fin_completo - inicio_completo
            dato = {
                "id": sesion.id,
                "fecha": sesion.fecha,
                "hora_inicio": sesion.hora_inicio,
                "hora_fin": sesion.hora_fin,
                "ejercicios": ejercicios_de_sesion,
                "duracion": str(duracion)
            }
            resultado.append(dato)
        return resultado
    finally:
        db.close()
    

    

@app.post("/ejercicios/{sesion_id}", response_model=EjercicioResponse)
def agregar_ejercicio(sesion_id: int, data: EjercicioBase):
    db = SessionLocal()
    try:
        nuevo = Ejercicio(nombre=data.nombre, reps=data.reps, series=data.series, sesion_id=sesion_id)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)  # <- esto asegura que el objeto tiene todos los datos actualizados
        return nuevo
    finally:
        db.close()


@app.post("/sesiones")
def agregar_sesion(data: SesionBase):
    db = SessionLocal()
    try:
        nuevo = Sesion(hora_inicio=data.hora_inicio)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    finally:
        db.close()


@app.get("/ejercicios/sesion/{sesion_id}",response_model=List[EjercicioResponse])
def buscar_por_id(sesion_id: int):
    db = SessionLocal()
    try:
        busqueda = db.query(Ejercicio).filter(Ejercicio.sesion_id == sesion_id).all()
        if busqueda:
            return busqueda
        raise HTTPException(status_code=404,detail="item not found")
    finally:
        db.close()
@app.get("/ejercicios/{id}",response_model=EjercicioResponse)
def buscar_por_id(id: int):
    db = SessionLocal()
    try:
        busqueda = db.query(Ejercicio).filter(Ejercicio.id == id).first()
        if busqueda:
            return busqueda
        raise HTTPException(status_code=404,detail="item not found")
    finally:
        db.close()
    

@app.delete("/ejercicios/{id}")
def eliminar_por_id(id: int):
    db = SessionLocal()
    try:
        busqueda = db.query(Ejercicio).filter(Ejercicio.id == id).first()
        if busqueda:
            db.delete(busqueda)
            db.commit()
            return {"mensaje": "eliminado"}
        raise HTTPException(status_code=404,detail="item not found")
    finally:
        db.close()
        


@app.put("/sesiones/{id}")
def actualizar_sesion(id: int, datos: SesionUpdate):
    db = SessionLocal()
    try:
        item = db.query(Sesion).filter(Sesion.id == id).first()
        if item:
            item.hora_fin = datos.hora_fin
            db.commit()
            return item
        raise HTTPException(status_code=404, detail="no encontrado")
    finally:
        db.close()
        
    
@app.get("/catalogo")
def mostrar_catalogo():
    db = SessionLocal()
    try:
        catalogo = db.query(Catalogo).all()
        return catalogo
    finally:
        db.close()
