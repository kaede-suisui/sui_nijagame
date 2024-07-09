# error_handling.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class SUIError(Exception):
    """SUIブロックチェーン関連のエラー"""
    pass

class GameLogicError(Exception):
    """ゲームロジック関連のエラー"""
    pass

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """エラーを処理し、ユーザーにフレンドリーなメッセージを送信します。"""
    try:
        raise context.error
    except SUIError as e:
        await update.message.reply_text("申し訳ありません。ブロックチェーンとの通信中にエラーが発生しました。しばらくしてからもう一度お試しください。")
        logger.error(f"SUIError: {str(e)}")
    except GameLogicError as e:
        await update.message.reply_text(f"ゲームエラー: {str(e)}")
        logger.error(f"GameLogicError: {str(e)}")
    except Exception as e:
        await update.message.reply_text("予期せぬエラーが発生しました。開発者に報告されます。")
        logger.error(f"Unexpected error: {str(e)}")

# main.py に以下を追加
from error_handling import error_handler, SUIError, GameLogicError

# application にエラーハンドラを追加
application.add_error_handler(error_handler)

# 各機能の実装内でエラーを適切に処理
async def start_battle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # バトル開始のロジック
        battle_id = await create_battle(player1, player2, weapon1, weapon2)
    except SUIError:
        raise
    except Exception as e:
        raise GameLogicError("バトルの開始に失敗しました。") from e

