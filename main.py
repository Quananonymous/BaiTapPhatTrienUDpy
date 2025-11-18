
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
        label {{ display: block; margin-top: 8px; margin-bottom: 4px; }}
        input, select {{ width: 100%; padding: 6px 8px; border-radius: 8px; border: 1px solid #4b5563; background: #020617; color: #e5e7eb; }}
        .row {{ display: flex; gap: 12px; }}
        .row > div {{ flex: 1; }}
        small {{ color: #9ca3af; }}
        hr {{ border-color: #1f2937; margin: 24px 0; }}
    </style>
</head>
<body>
    {body}
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    # Tóm tắt vị thế + bot
    summary_text = ""
    try:
        summary_text = bot_manager.get_position_summary()
    except Exception as e:
        summary_text = f"Không lấy được thống kê: {e}"

    # Danh sách bot hiện tại
    bot_rows = ""
    for bot_id, bot in bot_manager.bots.items():
        active = len(getattr(bot, "active_symbols", []))
        max_coins = getattr(bot, "max_coins", 1)
        bot_rows += f"""
            <div class="card">
                <h3>🤖 {bot_id}</h3>
                <p>Coin đang theo dõi: <b>{active}</b> / {max_coins}</p>
                <form method="post" action="/stop_bot">
                    <input type="hidden" name="bot_id" value="{bot_id}">
                    <button class="btn btn-danger" type="submit">⛔ Dừng bot này</button>
                </form>
            </div>
        """

    if not bot_rows:
        bot_rows = '<p><small>Hiện chưa có bot nào đang chạy.</small></p>'

    body = f"""
    <h1>🤖 Trading Bot – Web UI (không dùng Telegram)</h1>
    <p>Giao diện web đơn giản để điều khiển bot. Mobile app có thể gọi API JSON bên dưới.</p>

    <div class="card">
        <h2>📊 Thống kê nhanh</h2>
        <pre style="white-space: pre-wrap;">{summary_text}</pre>
        <form method="get" action="/summary">
            <button class="btn btn-secondary" type="submit">🔄 Làm mới thống kê (JSON)</button>
        </form>
    </div>

    <div class="card">
        <h2>➕ Tạo bot mới</h2>
        <form method="post" action="/add_bot">
            <div class="row">
                <div>
                    <label>Chế độ bot</label>
                    <select name="bot_mode">
                        <option value="static">🤖 Static – Chọn 1 coin cố định</option>
                        <option value="dynamic">🔄 Dynamic – Tự tìm coin</option>
                    </select>
                    <small>Dynamic: để trống Symbol, bot tự chọn coin theo RSI + volume.</small>
                </div>
                <div>
                    <label>Symbol (ví dụ: XRPUSDC)</label>
                    <input type="text" name="symbol" placeholder="XRPUSDC (để trống nếu Dynamic)">
                </div>
            </div>

            <div class="row">
                <div>
                    <label>Đòn bẩy (leverage, vd 10)</label>
                    <input type="number" name="lev" value="10" min="1" max="125" required>
                </div>
                <div>
                    <label>% số dư cho mỗi lệnh</label>
                    <input type="number" name="percent" value="5" min="1" max="100" step="0.1" required>
                </div>
            </div>

            <div class="row">
                <div>
                    <label>TP %</label>
                    <input type="number" name="tp" value="50" min="1" step="1" required>
                </div>
                <div>
                    <label>SL % (0 = tắt SL cố định)</label>
                    <input type="number" name="sl" value="0" min="0" step="1" required>
                </div>
            </div>

            <div class="row">
                <div>
                    <label>ROI trigger % (0 = tắt)</label>
                    <input type="number" name="roi_trigger" value="0" min="0" step="1">
                </div>
                <div>
                    <label>Số coin tối đa bot quản lý</label>
                    <input type="number" name="bot_count" value="3" min="1" max="20" required>
                </div>
            </div>

            <br>
            <button class="btn btn-primary" type="submit">🚀 Tạo bot</button>
        </form>
    </div>

    <div class="card">
        <h2>📋 Danh sách bot</h2>
        {bot_rows}
        <hr>
        <form method="post" action="/stop_all_bots" style="display:inline-block;margin-right:8px;">
            <button class="btn btn-danger" type="submit">🛑 Dừng TẤT CẢ bot</button>
        </form>
        <form method="post" action="/stop_all_coins" style="display:inline-block;">
            <button class="btn btn-secondary" type="submit">⛔ Chỉ dừng toàn bộ COIN</button>
        </form>
    </div>
    """

    return html_page("Trading Bot Web UI", body)


@app.post("/add_bot", response_class=HTMLResponse)
async def add_bot(
    bot_mode: str = Form("static"),
    symbol: str = Form(""),
    lev: int = Form(...),
    percent: float = Form(...),
    tp: float = Form(...),
    sl: float = Form(...),
    roi_trigger: float = Form(0),
    bot_count: int = Form(1),
):
    # Chuẩn hóa dữ liệu
    symbol_val = symbol.strip().upper() or None
    roi_val = None if roi_trigger is None or float(roi_trigger) <= 0 else float(roi_trigger)

    ok = bot_manager.add_bot(
        symbol=symbol_val,
        lev=int(lev),
        percent=float(percent),
        tp=float(tp),
        sl=float(sl),
        roi_trigger=roi_val,
        strategy_type="Hệ-thống-RSI-Khối-lượng",
        bot_mode="dynamic" if bot_mode == "dynamic" else "static",
        bot_count=int(bot_count),
    )

    # Redirect về trang chủ
    if ok:
        return RedirectResponse(url="/", status_code=303)
    return HTMLResponse(html_page("Lỗi", "<h1>Không tạo được bot – kiểm tra API key / số dư / config.</h1><a href='/'>Quay lại</a>"), status_code=400)


@app.get("/summary", response_class=JSONResponse)
async def summary():
    """API JSON – mobile app có thể gọi để lấy thống kê."""
    try:
        text = bot_manager.get_position_summary()
    except Exception as e:
        text = f"Lỗi: {e}"
    return {"summary": text}


@app.get("/bots", response_class=JSONResponse)
async def bots():
    """API JSON – danh sách bot để mobile app hiển thị."""
    data = []
    for bot_id, bot in bot_manager.bots.items():
        data.append({
            "bot_id": bot_id,
            "active_coins": len(getattr(bot, "active_symbols", [])),
            "max_coins": getattr(bot, "max_coins", 1),
        })
    return {"bots": data}


@app.post("/stop_bot", response_class=HTMLResponse)
async def stop_bot(bot_id: str = Form(...)):
    bot_manager.stop_bot(bot_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/stop_all_bots", response_class=HTMLResponse)
async def stop_all_bots():
    bot_manager.stop_all()
    return RedirectResponse(url="/", status_code=303)


@app.post("/stop_all_coins", response_class=HTMLResponse)
async def stop_all_coins():
    bot_manager.stop_all_coins()
    return RedirectResponse(url="/", status_code=303)


# Chạy local: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
