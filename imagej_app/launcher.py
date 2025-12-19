import os
import sys
import time
import threading
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import subprocess
import socket

BACKEND_PORT = 8000
FRONTEND_PORT = 8080

# 既存インスタンスへ「ブラウザ開け」を伝える用
CONTROL_PORT = 8766

# ---- Windows Mutex（単一起動）----
def acquire_mutex(name: str) -> bool:
    """
    True: このプロセスが唯一のインスタンス
    False: すでに別インスタンスがいる
    """
    if not sys.platform.startswith("win"):
        # 非Windowsなら、あなたの port-lock 方式でもOK
        return True

    import ctypes
    from ctypes import wintypes

    ERROR_ALREADY_EXISTS = 183
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    kernel32.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
    kernel32.CreateMutexW.restype = wintypes.HANDLE

    h = kernel32.CreateMutexW(None, True, name)
    if not h:
        return True  # 失敗時は安全側で動かす（ここは好みでFalseでも良い）

    already = (ctypes.get_last_error() == ERROR_ALREADY_EXISTS)
    if already:
        # 既存がいるのでこのハンドルは閉じる
        kernel32.CloseHandle(h)
        return False

    # プロセスが生きてる間保持させる
    global _mutex_handle
    _mutex_handle = h
    return True


def port_is_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except OSError:
        return False


def run_frontend(frontend_dir: Path):
    os.chdir(frontend_dir)
    httpd = ThreadingHTTPServer(("127.0.0.1", FRONTEND_PORT), SimpleHTTPRequestHandler)
    httpd.serve_forever()


def run_backend(root_dir: Path):
    cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "127.0.0.1",
        "--port", str(BACKEND_PORT),
        "--workers", "1",
    ]
    subprocess.Popen(
        cmd,
        cwd=str(root_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
    )


# ---- 既存インスタンスへ通知（2回目以降）----
def notify_existing_instance():
    try:
        with socket.create_connection(("127.0.0.1", CONTROL_PORT), timeout=0.5) as s:
            s.sendall(b"OPEN\n")
    except OSError:
        # 既存が起動途中で制御ポートがまだのケースなど
        # その場合は最小限：既存URLを開くだけ
        webbrowser.open(f"http://127.0.0.1:{FRONTEND_PORT}/", new=0, autoraise=True)


def control_server_loop():
    """
    既存インスタンス側が待ち受けて、
    新規起動(2回目以降)から「OPEN」を受けたらブラウザを開く
    """
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", CONTROL_PORT))
    srv.listen(5)
    while True:
        conn, _ = srv.accept()
        try:
            data = conn.recv(1024)
            if b"OPEN" in data:
                webbrowser.open(f"http://127.0.0.1:{FRONTEND_PORT}/", new=0, autoraise=True)
        finally:
            try:
                conn.close()
            except Exception:
                pass


def open_browser_once(url: str):
    # 起動直後はフロントがまだ立ってないことがあるので少し待つ
    for _ in range(30):
        if port_is_open("127.0.0.1", FRONTEND_PORT):
            break
        time.sleep(0.2)
    webbrowser.open(url, new=0, autoraise=True)


def main():
    root = Path(__file__).resolve().parent
    frontend_dir = root / "frontend"

    # ★最重要：Mutexで単一起動
    if not acquire_mutex(r"Local\MyAppLauncherSingleton"):
        # 2回目以降は既存へ通知して即終了（＝多重起動を実害ゼロに）
        notify_existing_instance()
        return

    # ★既存へ通知を受け取る制御サーバ（唯一の起動者だけが動かす）
    threading.Thread(target=control_server_loop, daemon=True).start()

    # バックエンド・フロントエンド起動（必要なら）
    if not port_is_open("127.0.0.1", BACKEND_PORT):
        run_backend(root)

    if not port_is_open("127.0.0.1", FRONTEND_PORT):
        threading.Thread(target=run_frontend, args=(frontend_dir,), daemon=True).start()

    # ブラウザは唯一の起動者が1回だけ
    threading.Thread(
        target=open_browser_once,
        args=(f"http://127.0.0.1:{FRONTEND_PORT}/",),
        daemon=True
    ).start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
