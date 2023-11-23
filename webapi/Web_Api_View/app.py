from fastapi import Depends, FastAPI
from fastapi_utils.inferring_router import InferringRouter

from webapi.ImplementationControllers.BusinessLogicControllers.UserLogic import UserLogic
from webapi.Web_Api_View.UserController import UserController
from webapi.ImplementationControllers.StorageControllers.UserRepository import UserRepository

userLogic = UserLogic()
userController = UserController(userLogic)


app = FastAPI()
app.include_router(userController)
