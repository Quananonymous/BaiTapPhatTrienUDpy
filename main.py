
import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from trading_bot_lib import BotManager  # sử dụng lại toàn bộ logic bot hiện tại

# Lấy API key từ biến môi trường (bạn tự set trên Railway / local)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY") or os.getenv("BINANCE_API_KEY_FUTURES")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY") or os.getenv("BINANCE_SECRET_KEY_FUTURES")

# KHỞI TẠO BOT MANAGER KHÔNG DÙNG TELEGRAM
bot_manager = BotManager(
    api_key=BINANCE_API_KEY,
    api_secret=BINANCE_SECRET_KEY,
    telegram_bot_token=None,
    telegram_chat_id=None,
)

app = FastAPI(title="Trading Bot Web UI", version="1.0.0")


def html_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 16px; background-color: #0f172a; color: #e5e7eb; }}
        h1, h2, h3 {{ color: #facc15; }}
        a {{ color: #38bdf8; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .card {{ background: #020617; border-radius: 12px; padding: 16px 20px; margin-bottom: 16px; border: 1px solid #1f2937; }}
        .btn {{ display: inline-block; padding: 8px 14px; border-radius: 999px; border: none; cursor: pointer; font-weight: 600; }}
        .btn-primary {{ background: #22c55e; color: #0f172a; }}
        .btn-danger {{ background: #ef4444; color: white; }}
        .btn-secondary {{ background: #1f2937; color: #e5e7eb; }}
        form {{ margin-top: 12px; }}
        label {{ display: block; margin-top: 8px; margin-botto8080, reload=True)
