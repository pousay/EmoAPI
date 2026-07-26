from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from core.config import config
from routes import query_router, states_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router)
app.include_router(states_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        port=config.PORT,
        host=config.HOST,
    )
