from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from core.config import config

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def test():
    return "nice"


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        port=config.PORT,
        host=config.HOST,
    )
