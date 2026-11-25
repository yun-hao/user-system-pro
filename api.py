from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse


from models import ValidationError, UserNotFoundError, StorageError
from schemas import UserResponse, UserCreate, UserUpdate
from storage import  create_storage
from user_manager import UserManager

app = FastAPI()



manager = UserManager(create_storage())


@app.post('/users',response_model=UserResponse,status_code=201)
def create_user(payload:UserCreate):
    return manager.add_user(payload.name,payload.age, payload.email, payload.phone)

@app.get('/users',response_model=list[UserResponse])
def read_users():
    return manager.list_users()


@app.get('/users/{user_id}',response_model=UserResponse)
def read_user(user_id:int):
    return manager.get_user(user_id)

@app.patch('/users/{user_id}',response_model=UserResponse)
def update_user(user_id:int,payload:UserUpdate):
    return manager.update_user(user_id,payload.name, payload.age, payload.email, payload.phone)

@app.delete('/users/{user_id}',status_code=204)
def delete_user(user_id:int):
    manager.delete_user(user_id)


@app.exception_handler(ValidationError)
def validation_error_handler(request:Request, exc:ValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(UserNotFoundError)
def get_user_error_handler(request:Request, exc:UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(StorageError)
def storage_error_handler(request:Request, exc:StorageError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})