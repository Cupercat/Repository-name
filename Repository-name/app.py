from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from .db import engine,Base
from .app_auth.auth_router import app as auth_app # type: ignore
from .seller.seller_router import app as seller_app # type: ignore
from .client.client_router import app as client_app # type: ignore

from .admin_panel.admin_router import app as admin_app # type: ignore

from .prodcuts.products_models import Product, Category, SubCategory # type: ignore
from .seller.seller_models import SellerProfile, SellerProduct # type: ignore
from .client.client_models import ClientBacket # type: ignore


app = FastAPI()

# routers
app.include_router(auth_app)
app.include_router(seller_app)
app.include_router(client_app)


# ADMIN PANEL

app.include_router(admin_app)

# CORS

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type",
                   "Set-Cookie",
                   "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)




# init project
@app.get("/init")
async def create_db():
    
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.drop_all)
        except:
            pass
        await  conn.run_sync(Base.metadata.create_all)