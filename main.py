#main.py
from fastapi import FastAPI
import read_email
from db import Base, engine

app = FastAPI()

app.include_router(read_email.router)

Base.metadata.create_all(engine)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8889)
