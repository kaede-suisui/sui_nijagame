# security.py

import hashlib
import hmac
import time
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

SECRET_KEY = "your_secret_key_here"  # 安全な方法で管理してください

def generate_token(user_id: int) -> str:
    timestamp = int(time.time())
    message = f"{user_id}:{timestamp}"
    signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"{message}:{signature}"

def verify_token(token: str) -> bool:
    try:
        message, signature = token.rsplit(":", 1)
        user_id, timestamp = message.split(":", 1)
        expected_signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected_signature) and (int(time.time()) - int(timestamp)) < 3600
    except:
        return False

def require_wallet_connection(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_session = await get_user_session(context, update.effective_user.id)
        if not user_session.wallet_address:
            await update.message.reply_text("この操作にはウォレットの接続が必要です。設定メニューから接続してください。")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# main.py の各ハンドラー内で使用
@require_wallet_connection
async def start_battle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # バトル開始のロジック...

# トークンを使用した認証
async def authenticate_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    token = generate_token(user_id)
    await update.message.reply_text(f"認証トークン: {token}\n\nこのトークンを使用して認証してください。")

async def verify_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    token = context.args[0] if context.args else None
    if token and verify_token(token):
        await update.message.reply_text("認証成功！")
    else:
        await update.message.reply_text("認証失敗。有効なトークンを使用してください。")

