from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db.db_user_app import (
    validate_user,
    insert_user,
    get_all_user,
    get_user_permissions_by_email,
    get_user_roles_by_email,
)
from db.db_pemrisos import obtener_todos_los_permisos
from db.db_usuario_roles import insertar_usuario_rol
from db.db_roles import obtener_todos_los_roles

app = FastAPI(title="Rintin Backend")

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    authenticated: bool

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str
    role_id: int

class RegisterResponse(BaseModel):
    user_id: int

@app.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    if validate_user('prod', data.email, data.password):
        return {"authenticated": True}
    return {"authenticated": False}

@app.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest):
    user_id = insert_user('prod', data.email, data.password)
    if user_id is None:
        raise HTTPException(status_code=400, detail="Unable to create user")
    insertar_usuario_rol(user_id, data.role_id)
    return {"user_id": user_id}


class User(BaseModel):
    id: int
    email: str


class Permission(BaseModel):
    nombre_permiso: str


class UserRole(BaseModel):
    rol_id: int
    nombre_rol: str


class Role(BaseModel):
    rol_id: int
    nombre_rol: str
    descripcion: str | None = None


@app.get("/users", response_model=list[User])
def list_users():
    return get_all_user()


@app.get("/users/{email}/permissions", response_model=list[Permission])
def user_permissions(email: str):
    return get_user_permissions_by_email(email)


@app.get("/users/{email}/roles", response_model=list[UserRole])
def user_roles(email: str):
    return get_user_roles_by_email(email)


@app.get("/roles", response_model=list[Role])
def list_roles():
    return [
        {
            "rol_id": r[0],
            "nombre_rol": r[1],
            "descripcion": r[2] if len(r) > 2 else None,
        }
        for r in obtener_todos_los_roles()
    ]


class SystemPermission(BaseModel):
    permiso_id: int
    ops_id_fk: int
    nombre_permiso: str
    descripcion: str | None = None


@app.get("/permissions", response_model=list[SystemPermission])
def list_permissions():
    return [
        {
            "permiso_id": p[0],
            "ops_id_fk": p[1],
            "nombre_permiso": p[2],
            "descripcion": p[3] if len(p) > 3 else None,
        }
        for p in obtener_todos_los_permisos()
    ]

