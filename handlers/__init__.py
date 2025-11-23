from handlers.auth import router as auth_router
from handlers.root import router as root_router
from handlers.service import router as service_router

routers = [auth_router, root_router, service_router]