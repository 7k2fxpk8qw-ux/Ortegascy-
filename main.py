from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Ortegascy TON App")

# Serve static React build files if they exist
dist_path = os.path.join(os.path.dirname(__file__), "dist")
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

    @app.get("/tonconnect-manifest.json")
    async def manifest():
        return FileResponse(os.path.join(dist_path, "tonconnect-manifest.json"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        index = os.path.join(dist_path, "index.html")
        return FileResponse(index)
else:
    @app.get("/")
    async def root():
        return {"message": "Ortegascy TON App - React build not found. Run 'npm run build' first."}
