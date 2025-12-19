from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tempfile, os, re
from .imagej_pipeline import run_pipeline


app = FastAPI()

# フロントが別ホスト/別ポートでも呼べるように（開発中だけ緩め）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

@app.get("/")
def root():
    return {"ok": True, "hint": "open /docs"}

@app.post("/api/process")
async def process(files: list[UploadFile] = File(...), speed: int = Form(20)):
    workdir = tempfile.mkdtemp(prefix="imgseq_")

    try:
        for f in files:
            with open(os.path.join(workdir, f.filename), "wb") as w:
                w.write(await f.read())

        out_gif = os.path.join(workdir, "out.gif")
        run_pipeline(workdir, out_gif, speed=int(speed))

        return FileResponse(out_gif, media_type="image/gif", filename="out.gif")
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)



from fastapi import UploadFile, File, Form
import re

def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

@app.post("/api/process")
async def process(
    files: list[UploadFile] = File(...),
    speed: int = Form(20),
):
    if not files:
        return {"ok": False, "error": "no files"}

    names = sorted([f.filename for f in files], key=natural_key)
    return {
        "ok": True,
        "count": len(names),
        "first": names[0],
        "last": names[-1],
        "speed": speed
    }

