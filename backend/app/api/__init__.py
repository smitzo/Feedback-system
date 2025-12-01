from .auth import router as auth
from .health import router as health
from .people import router as people

routers = [health, auth, people]
