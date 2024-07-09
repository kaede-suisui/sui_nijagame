# battle_system.py

import random
from typing import Dict, List
from sui_sdk import SuiClient, SuiConfig
from user_session import get_user_session

sui_config = SuiConfig.from_network('testnet')
sui_client = SuiClient(sui_config)

class BattleSystem:
    def __init__(self):
        self.active_battles: Dict[str, Dict] = {}

    async def create_battle(self, player1: str, player2: str, weapon1: str, weapon2: str) -> str:
        battle_id = f"battle_{random.randint(1000, 9999)}"
        self.active_battles[battle_id] = {
            "player1": player1,
            "player2": player2,
            "weapon1": weapon1,
            "weapon2": weapon2,
            "current_round": 0,
            "max_rounds": 3,
            "player1_wins": 0,
            "player2_wins": 0,
            "moves": {"player1": None, "player2": None}
        }
        return battle_id

    async def make_move(self, battle_id: str, player: str, move: str) -> Dict:
        battle = self.active_battles.get(battle_id)
        if not battle:
            raise ValueError("Invalid battle ID")

        if player not in [battle["player1"], battle["player2"]]:
            raise ValueError("Invalid player for this battle")

        player_key = "player1" if player == battle["player1"] else "player2"
        battle["moves"][player_key] = move

        if all(battle["moves"].values()):
            return await self.resolve_round(battle_id)
        return {"status": "waiting", "message": "待機中: 相手の手を待っています"}

    async def resolve_round(self, battle_id: str) -> Dict:
        battle = self.active_battles[battle_id]
        move1, move2 = battle["moves"]["player1"], battle["moves"]["player2"]
        weapon1, weapon2 = battle["weapon1"], battle["weapon2"]

        # ここで忍具の効果を適用
        power1 = await self.calculate_power(move1, weapon1)
        power2 = await self.calculate_power(move2, weapon2)

        result = self.determine_winner(move1, move2, power1, power2)
        battle["current_round"] += 1

        if result == "player1":
            battle["player1_wins"] += 1
        elif result == "player2":
            battle["player2_wins"] += 1

        battle["moves"] = {"player1": None, "player2": None}

        if battle["player1_wins"] == 2 or battle["player2_wins"] == 2 or battle["current_round"] == battle["max_rounds"]:
            return await self.end_battle(battle_id)

        return {
            "status": "ongoing",
            "current_round": battle["current_round"],
            "player1_wins": battle["player1_wins"],
            "player2_wins": battle["player2_wins"],
            "message": f"ラウンド {battle['current_round']} 終了"
        }

    async def calculate_power(self, move: str, weapon: str) -> int:
        # 忍具の効果を計算（実際にはSUIブロックチェーンから忍具の情報を取得）
        base_power = {"rock": 100, "paper": 100, "scissors": 100}[move]
        weapon_power = await sui_client.get_object(weapon)  # 簡略化
        return base_power + weapon_power

    def determine_winner(self, move1: str, move2: str, power1: int, power2: int) -> str:
        moves = {"rock": 0, "paper": 1, "scissors": 2}
        if moves[move1] == moves[move2]:
            return "player1" if power1 > power2 else "player2"
        return "player1" if (moves[move1] - moves[move2]) % 3 == 1 else "player2"

    async def end_battle(self, battle_id: str) -> Dict:
        battle = self.active_battles[battle_id]
        winner = "player1" if battle["player1_wins"] > battle["player2_wins"] else "player2"
        
        # 結果をブロックチェーンに記録
        await sui_client.move_call(
            'record_battle_result',
            [battle[winner], battle["player1_wins"], battle["player2_wins"]]
        )

        del self.active_battles[battle_id]
        return {
            "status": "ended",
            "winner": battle[winner],
            "player1_wins": battle["player1_wins"],
            "player2_wins": battle["player2_wins"],
            "message": f"バトル終了！勝者: {battle[winner]}"
        }

battle_system = BattleSystem()

# main.py での使用例
async def start_battle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_session = await get_user_session(context, update.effective_user.id)
    opponent = await find_opponent(update.effective_user.id)  # マッチメイキング関数（要実装）
    battle_id = await battle_system.create_battle(
        update.effective_user.id,
        opponent,
        user_session.selected_weapon,
        await get_opponent_weapon(opponent)  # 対戦相手の武器を取得する関数（要実装）
    )
    user_session.current_battle = battle_id
    await update.message.reply_text("対戦相手が見つかりました！バトルを開始します。")
    await show_battle_options(update, context)

async def handle_battle_move(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_session = await get_user_session(context, update.effective_user.id)
    move = update.callback_query.data
    result = await battle_system.make_move(user_session.current_battle, update.effective_user.id, move)
    
    if result['status'] == 'waiting':
        await update.callback_query.edit_message_text(result['message'])
    elif result['status'] == 'ongoing':
        await update.callback_query.edit_message_text(f"{result['message']}\n現在の状況: {result['player1_wins']} - {result['player2_wins']}")
        await show_battle_options(update, context)
    elif result['status'] == 'ended':
        await update.callback_query.edit_message_text(result['message'])
        # 報酬の付与やランキングの更新などの処理を行う

async def show_battle_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("✊ 岩", callback_data='rock'),
         InlineKeyboardButton("✋ 紙", callback_data='paper'),
         InlineKeyboardButton("✌️ はさみ", callback_data='scissors')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("あなたの手を選んでください：", reply_markup=reply_markup)

