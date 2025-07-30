from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db.db_user_app import validate_user, insert_user
from db.db_usuario_roles import insertar_usuario_rol

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

