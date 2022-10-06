import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from storage.web.api import api_router

if __name__ == "__main__":
    app = FastAPI(title="MerkleBot Storage")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    uvicorn.run(app, host="0.0.0.0", port=8000)
