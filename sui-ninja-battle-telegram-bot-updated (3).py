# main.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from battle_integration import start_battle, handle_battle_choice
from nft_integration import manage_weapons
from ranking_integration import show_ranking, check_status

# ボットトークンを設定します（実際のトークンに置き換えてください）
TOKEN = "YOUR_BOT_TOKEN_HERE"

# ロギングの設定
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ボットの開始コマンドを処理し、メインメニューを表示します。"""
    keyboard = [
        [InlineKeyboardButton("🏆 バトル開始", callback_data='start_battle')],
        [InlineKeyboardButton("🗡 忍具管理", callback_data='manage_weapons')],
        [InlineKeyboardButton("📊 ステータス確認", callback_data='check_status')],
        [InlineKeyboardButton("🏅 ランキング", callback_data='show_ranking')],
        [InlineKeyboardButton("⚙ 設定", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('SUI忍者バトルへようこそ！操作を選択してください：', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ボタンのコールバックを処理します。"""
    query = update.callback_query
    await query.answer()

    if query.data == 'start_battle':
        await start_battle(update, context)
    elif query.data == 'manage_weapons':
        await manage_weapons(update, context)
    elif query.data == 'check_status':
        await check_status(update, context)
    elif query.data == 'show_ranking':
        await show_ranking(update, context)
    elif query.data == 'settings':
        await settings(update, context)
    elif query.data in ['rock', 'paper', 'scissors']:
        await handle_battle_choice(update, context)

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """設定画面を表示します。"""
    query = update.callback_query
    await query.edit_message_text("設定機能は開発中です。もうしばらくお待ちください。")

def main() -> None:
    """ボットを起動します。"""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # ボットの実行を開始
    application.run_polling()

if __name__ == '__main__':
    main()

