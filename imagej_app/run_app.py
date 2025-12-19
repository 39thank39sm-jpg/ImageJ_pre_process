import threading
import time
import webbrowser
import uvicorn

def open_browser():
    # サーバー起動を少し待ってからブラウザを開く
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    # ブラウザ自動起動
    threading.Thread(target=open_browser, daemon=True).start()

    # FastAPI 起動
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,   # exeではFalse
        log_level="info"
    )
