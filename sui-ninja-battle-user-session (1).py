# user_session.py

from telegram.ext import ContextTypes

class UserSession:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.current_battle = None
        self.selected_weapon = None
        self.wallet_address = None

async def get_user_session(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> UserSession:
    if 'user_sessions' not in context.bot_data:
        context.bot_data['user_sessions'] = {}
    
    if user_id not in context.bot_data['user_sessions']:
        context.bot_data['user_sessions'][user_id] = UserSession(user_id)
    
    return context.bot_data['user_sessions'][user_id]

# main.py の各ハンドラー内で使用
async def start_battle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_session = await get_user_session(context, update.effective_user.id)
    # ユーザーセッションを使用してバトル情報を保存
    user_session.current_battle = await create_battle(...)

async def handle_battle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_session = await get_user_session(context, update.effective_user.id)
    # ユーザーセッションから現在のバトル情報を取得
    battle_id = user_session.current_battle
    # バトルの処理...

