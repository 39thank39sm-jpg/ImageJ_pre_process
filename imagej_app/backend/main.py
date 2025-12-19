from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tempfile, os, re

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

@app.post("/api/process")
async def process(
    files: list[UploadFile] = File(...),
    speed: int = Form(20),
):
    if not files:
        return JSONResponse({"error": "no files"}, status_code=400)

    # 一時フォルダへ保存（ImageJ側に渡しやすい）
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        paths = []
        for f in files:
            p = tmp / f.filename
            p.write_bytes(await f.read())
            paths.append(p)

        # ファイル名でソート（連番想定）
        paths = sorted(paths, key=lambda p: natural_key(p.name))

        # ここに ImageJ API（pyimagej）で
        # Import Image Sequence -> Enhance Contrast -> Invert -> Animation speed -> GIF保存
        # を入れる（次のステップであなたの処理をそのまま実装する）

        # いまは「実装枠」だけ用意：ダミーでエラー返す
        return JSONResponse({
            "message": "backend connected",
            "files": len(paths),
            "speed": speed,
            "note": "ここにImageJ処理を実装します"
        })
    

@app.get("/")
def health():
    return {"ok": True, "message": "backend is running"}

@app.get("/api/ping")
def ping():
    return {"ok": True, "message": "pong"}


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

