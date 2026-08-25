from fastapi import FastAPI
from app.routers import clients_router, availability_router, payment_router, phoneVerif_routers, reservation_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    # "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(clients_router.router)
app.include_router(availability_router.router)
app.include_router(payment_router.router)
app.include_router(phoneVerif_routers.router)
app.include_router(reservation_router.router)
