from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

from routes import router
app.include_router(router)



hosts_list = ["http://localhost:5173", "http://localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=hosts_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

