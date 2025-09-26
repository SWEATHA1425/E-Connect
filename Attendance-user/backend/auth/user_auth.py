from fastapi import FastAPI, Depends
from .auth_bearer import JWTBearer
from .auth_handler import signJWT

app = FastAPI()
user_jwt_bearer = JWTBearer(role="user")

@app.get("/clock-records/{userid}")
async def user_only_route(token: str = Depends(user_jwt_bearer)):
    return {"message": "This is a user-only route"}

@app.get("/leave-History/{userid}/")
async def user_only_route(token: str = Depends(user_jwt_bearer)):
    return {"message": "This is a user-only route"}

@app.get("/Remote-History/{userid}")
async def user_only_route(token: str = Depends(user_jwt_bearer)):
    return {"message": "This is a user-only route"}
<<<<<<< HEAD

=======
>>>>>>> feature-sweatha-attendance
