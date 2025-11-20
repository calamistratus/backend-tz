from handlers.auth import router as auth_router
from handlers.root import router as root_router
from handlers.ping import router as ping_router

routers = [auth_router, root_router, ping_router]