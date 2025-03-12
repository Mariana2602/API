#Alejandro Lopez 30.914.440
#Yexibel Aguero 31.268.552
#Mariana Lopez 30.913.839
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    conn = sqlite3.connect("usuarios.db")
    conn.row_factory = sqlite3.Row  
    return conn


class Usuario(BaseModel):
    nombre: str
    email: str
    password: str

def hash_pwd(password: str):
    return pwd_context.hash(password)

def validar_pwd(password_plana: str, hashed_password: str):
    return pwd_context.verify(password_plana, hashed_password)

@app.get("/usuarios/")
def obtener_usuarios():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email FROM usuarios")
    usuarios = cursor.fetchall()
    return [dict(usuario) for usuario in usuarios]

@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return dict(usuario)


@app.post("/usuarios/")
def crear_usuario(usuario: Usuario):
    conn = get_db()
    cursor = conn.cursor()
    hashed_password = hash_pwd(usuario.password)

    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
            (usuario.nombre, usuario.email, hashed_password),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    return {"mensaje": "Usuario creado"}


@app.delete("/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario eliminado"}


@app.post("/login/")
def login(email: str, password: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()

    if usuario is None or not validar_pwd(password, usuario["password"]):
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")

    return {"mensaje": "Inicio de sesión exitoso"}