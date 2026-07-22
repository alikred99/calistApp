from fastapi import FastAPI, HTTPException, Depends
from models import Ejercicio, Sesion, Catalogo, Usuario, Rutina, RutinaEjercicio
from pydantic import BaseModel, Field, field_serializer
from databases import SessionLocal
from datetime import date, time, datetime
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from auth import hashear_password, verificar_password, crear_token, obtener_usuario_actual
from fastapi.security import OAuth2PasswordRequestForm
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UsuarioRegistro(BaseModel):
    usuario: str
    contrasena: str = Field(min_length=8)

class UsuarioResponse(BaseModel):
    id: int
    usuario: str
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
class UsuarioLogin(BaseModel):
    usuario: str
    contrasena: str = Field(min_length=8)

    
class EjercicioBase(BaseModel):
    nombre: str
    reps: int = Field(gt=0)
    series: int = Field(gt=0)


class EjercicioEnRutina(BaseModel):
    id_ejercicios: int
    orden: int
    reps: int = Field(gt=0)
    series: int = Field(gt=0)


class RutinaCrear(BaseModel):
    nombre: str
    ejercicios: list[EjercicioEnRutina]

class SesionBase(BaseModel):
    hora_inicio: time
    rutina_id: int


class SesionUpdate(BaseModel):
    hora_fin: time
class EjercicioResponse(BaseModel):
    id: int
    nombre: str
    reps: int
    series: int
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

@app.post("/registro", response_model=UsuarioResponse)
def registrar_usuario(data: UsuarioRegistro):
    db = SessionLocal()
    try:
        
        existe = db.query(Usuario).filter(Usuario.usuario == data.usuario).first()
        if existe:
            raise HTTPException(status_code=400, detail="usuario ya existe")
        else:
            contrasena_hasheada = hashear_password(data.contrasena)
            nuevo = Usuario(usuario = data.usuario, contrasena=contrasena_hasheada)
            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)
            return nuevo
    finally:
        db.close()


@app.post("/login", response_model=TokenResponse)
def iniciar_usuario(data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter(Usuario.usuario == data.username).first()
        if not existe:
            raise HTTPException(status_code=401, detail="Acceso no autorizado")
        else:
            contrasena = data.password
            if verificar_password(contrasena, existe.contrasena):
                token = crear_token({"sub": str(existe.id)})
                return {"access_token": token, "token_type": "bearer"}
            else:
                raise HTTPException(status_code=401, detail="Acceso no autorizado")
    finally:
        db.close()


@app.post("/rutinas")
def crear_rutinas(data: RutinaCrear):
    db = SessionLocal()
    try:
        nuevo = Rutina(nombre=data.nombre)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        for item in data.ejercicios:
            nueva_relacion = RutinaEjercicio(
                id_rutina = nuevo.id,
                id_ejercicios = item.id_ejercicios,
                orden = item.orden,
                reps = item.reps,
                series = item.series
            )
            db.add(nueva_relacion)
        db.commit()
        return nuevo
    finally:
        db.close()
@app.get("/rutinas")
def listar_rutinas():
    db = SessionLocal()
    try:
        rutinas = db.query(Rutina).all()
        resultado = []
        for rutina in rutinas:
            relaciones = db.query(RutinaEjercicio).filter(RutinaEjercicio.id_rutina == rutina.id).all()
            lista_ejercicios = []
            for relacion in relaciones:
                ejercicio_catalogo = db.query(Catalogo).filter(Catalogo.id == relacion.id_ejercicios).first()
                lista_ejercicios.append({
                    "nombre": ejercicio_catalogo.nombre,
                    "orden": relacion.orden,
                    "reps": relacion.reps,
                    "series": relacion.series
                })
            dato = {
                    "id": rutina.id,
                    "nombre": rutina.nombre,
                    "ejercicios": lista_ejercicios
                }
            resultado.append(dato)
        return resultado
    finally:
        db.close()
    
@app.delete("/rutinas/{id}")
def eliminar_rutina_por_id(id: int):
    db = SessionLocal()
    try:
        rutina = db.query(Rutina).filter(Rutina.id==id).first()
        if rutina:
            db.query(RutinaEjercicio).filter(RutinaEjercicio.id_rutina == id).delete()
            db.delete(rutina)
            db.commit()
            return {"mensaje": "eliminado"}
        raise HTTPException(status_code=404,detail="item not found")
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
def listar_historial_sesiones(usuario_actual=Depends(obtener_usuario_actual)):
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
        db.refresh(nuevo)  # <- asegura que tenga los datos actualizados
        return nuevo
    finally:
        db.close()


@app.post("/sesiones")
def agregar_sesion(data: SesionBase):
    db = SessionLocal()
    try:
        nuevo = Sesion(hora_inicio=data.hora_inicio, rutina_id=data.rutina_id)
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    finally:
        db.close()




@app.get("/ejercicios/sesion/{sesion_id}",response_model=List[EjercicioResponse])
def buscar_sesion_por_id(sesion_id: int):
    db = SessionLocal()
    try:
        busqueda = db.query(Ejercicio).filter(Ejercicio.sesion_id == sesion_id).all()
        if busqueda:
            return busqueda
        raise HTTPException(status_code=404,detail="item not found")
    finally:
        db.close()
@app.get("/ejercicios/{id}",response_model=EjercicioResponse)
def buscar_ejercicio_por_id(id: int):
    db = SessionLocal()
    try:
        busqueda = db.query(Ejercicio).filter(Ejercicio.id == id).first()
        if busqueda:
            return busqueda
        raise HTTPException(status_code=404,detail="item not found")
    finally:
        db.close()

@app.get("/rutina/{id}")
def buscar_rutina_por_id(id: int):
    db = SessionLocal()
    try:
        rutina = db.query(Rutina).filter(Rutina.id == id).first()
        if rutina:
            relaciones = db.query(RutinaEjercicio).filter(RutinaEjercicio.id_rutina == rutina.id).all()
            lista_ejercicios = []
            for relacion in relaciones:
                ejercicio_catalogo = db.query(Catalogo).filter(Catalogo.id == relacion.id_ejercicios).first()
                lista_ejercicios.append({
                    "nombre": ejercicio_catalogo.nombre,
                    "orden": relacion.orden,
                    "reps": relacion.reps,
                    "series": relacion.series
                    })
            dato = {
                "id": rutina.id,
                "nombre": rutina.nombre,
                "ejercicios": lista_ejercicios
                }
            return dato
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
