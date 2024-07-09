# ranking_seasons.py 

from datetime import datetime, timedelta
from typing import List, Dict
from sui_sdk import SuiClient, SuiConfig

sui_config = SuiConfig.from_network('testnet')
sui_client = SuiClient(sui_config)

class RankingSystem:
    def __init__(self):
        self.current_season = 1
        self.season_start = datetime.now()
        self.season_duration = timedelta(days=30)  # 1シーズン30日

    async def update_ranking(self, player: str, points: int) -> None:
        await sui_client.move_call(
            'update_player_ranking',
            [player, points, self.current_season],
            gas_budget=1000
        )

    async def get_leaderboard(self, top_n: int = 10) -> List[Dict]:
        result = await sui_client.move_call(
            'get_leaderboard',
            [self.current_season, top_n],
            gas_budget=1000
        )
        return result.leaderboard

    async def check_season_end(self) -> bool:
        if datetime.now() - self.season_start >= self.season_duration:
            await self.end_season()
            return True
        return False

    async def end_season(self) -> None:
        # シーズン終了処理
        await sui_client.move_call(
            'end_season',
            [self.current_season],
            gas_budget=2000
        )
        
        # 報酬配布
        await self.distribute_season_rewards()
        
        # 新シーズン開始
        self.current_season += 1
        self.season_start = datetime.now()
        
        await sui_client.move_call(
            'start_new_season',
            [self.current_season],
            gas_budget=1000
        )

    async def distribute_season_rewards(self) -> None:
        top_players = await self.get_leaderboard(100)  # 上位100人に報酬を配布
        for rank, player in enumerate(top_players, 1):
            reward = self.calculate_reward(rank)
            await sui_client.move_call(
                'distribute_season_reward',
                [player['address'], reward, self.current_season],
                gas_budget=1000
            )

    def calculate_reward(self, rank: int) -> int:
        # ランクに応じた報酬計算ロジック
        if rank == 1:
            return 10000  # 1位の報酬
        elif rank <= 10:
            return 5000  # 2-10位の報酬
        elif rank <= 50:
            return 2000  # 11-50位の報酬
        else:
            return 1000  # 51-100位の報酬

ranking_system = RankingSystem()

# イベント管理システム
class EventSystem:
    def __init__(self):
        self.current_event = None
        self.event_end_time = None

    async def start_event(self, event_type: str, duration: timedelta) -> None:
        self.current_event = event_type
        self.event_end_time = datetime.now() + duration
        
        await sui_client.move_call(
            'start_event',
            [event_type, int(self.event_end_time.timestamp())],
            gas_budget=1000
        )

    async def end_event(self) -> None:
        if self.current_event and datetime.now() >= self.event_end_time:
            await sui_client.move_call(
                'end_event',
                [self.current_event],
                gas_budget=1000
            )
            
            await self.distribute_event_rewards()
            self.current_event = None
            self.event_end_time = None

    async def distribute_event_rewards(self) -> None:
        event_leaderboard = await sui_client.move_call(
            'get_event_leaderboard',
            [self.current_event],
            gas_budget=1000
        )
        
        for rank, player in enumerate(event_leaderboard, 1):
            reward = self.calculate_event_reward(rank)
            await sui_client.move_call(
                'distribute_event_reward',
                [player['address'], reward, self.current_event],
                gas_budget=1000
            )

    def calculate_event_reward(self, rank: int) -> int:
        # イベントランクに応じた報酬計算ロジック
        if rank == 1:
            return 5000  # 1位の報酬
        elif rank <= 5:
            return 2500  # 2-5位の報酬
        elif rank <= 20:
            return 1000  # 6-20位の報酬
        else:
            return 500  # 21位以下の報酬

event_system = EventSystem()

# main.py での使用例
async def check_rankings_and_events(context: ContextTypes.DEFAULT_TYPE) -> None:
    # 定期的に実行される関数（例：1時間ごと）
    await ranking_system.check_season_end()
    await event_system.end_event()

    if not event_system.current_event:
        # ランダムで新しいイベントを開始
        event_types = ["ダブルバトル", "エリートチャレンジ", "忍具マスター"]
        new_event = random.choice(event_types)
        await event_system.start_event(new_event, timedelta(days=3))
        
        # すべてのユーザーに通知
        for user_id in get_all_users():  # すべてのユーザーIDを取得する関数（要実装）
            await context.bot.send_message(
                chat_id=user_id,
                text=f"新しいイベント「{new_event}」が開始されました！参加して特別報酬をゲットしよう！"
            )

async def show_rankings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    leaderboard = await ranking_system.get_leaderboard()
    ranking_text = "🏆 シーズンランキング 🏆\n\n"
    for i, player in enumerate(leaderboard, 1):
        ranking_text += f"{i}. {player['name']} - {player['points']}ポイント\n"
    
    if event_system.current_event:
        event_leaderboard = await sui_client.move_call(
            'get_event_leaderboard',
            [event_system.current_event],
            gas_budget=1000
        )
        ranking_text += f"\n🌟 イベント「{event_system.current_event}」ランキング 🌟\n\n"
        for i, player in enumerate(event_leaderboard[:5], 1):
            ranking_text += f"{i}. {player['name']} - {player['points']}ポイント\n"
    
    await update.message.reply_text(ranking_text)

# Application に定期タスクを追加
application.job_queue.run_repeating(check_rankings_and_events, interval=3600)  # 1時間ごとに実行

