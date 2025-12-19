import os
import sys
import time
import threading
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import subprocess

BACKEND_PORT = 8000
FRONTEND_PORT = 8080

def run_frontend(frontend_dir: Path):
    os.chdir(frontend_dir)
    httpd = ThreadingHTTPServer(("127.0.0.1", FRONTEND_PORT), SimpleHTTPRequestHandler)
    httpd.serve_forever()

def run_backend(backend_dir: Path):
    # uvicornを "python -m" で起動（PATH問題回避）
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "127.0.0.1",
        "--port", str(BACKEND_PORT),
    ]
    subprocess.Popen(cmd, cwd=str(backend_dir))

def main():
    root = Path(__file__).resolve().parent
    backend_dir = root / "backend"
    frontend_dir = root / "frontend"

    # 1) backend
    run_backend(backend_dir)

    # 2) frontend（別スレッド）
    t = threading.Thread(target=run_frontend, args=(frontend_dir,), daemon=True)
    t.start()

    # 3) ブラウザを開く
    time.sleep(0.6)
    webbrowser.open(f"http://127.0.0.1:{FRONTEND_PORT}/")

    # exeが即終了しないように待機
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
