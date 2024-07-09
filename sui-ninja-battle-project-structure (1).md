```
sui_ninja_battle/
│
├── smart_contracts/
│   ├── nft.move
│   ├── battle.move
│   ├── player_stats.move
│   ├── ranking.move
│   └── game_state.move
│
├── telegram_bot/
│   ├── main.py
│   ├── bot_handlers.py
│   ├── ui_components.py
│   ├── battle_system.py
│   ├── nft_management.py
│   ├── ranking_system.py
│   ├── event_system.py
│   ├── user_session.py
│   └── localization.py
│
├── utils/
│   ├── sui_integration.py
│   └── error_handling.py
│
├── tests/
│   ├── test_battle_system.py
│   ├── test_nft_management.py
│   ├── test_ranking_system.py
│   └── test_event_system.py
│
├── locales/
│   ├── en.yml
│   ├── ja.yml
│   └── ... (other language files)
│
├── README.md
├── requirements.txt
└── .gitignore
```

主要なファイルの内容：

1. `smart_contracts/game_state.move`:
   このファイルには、先ほど提供したMoveの実装が含まれます。

2. `telegram_bot/main.py`:

```python
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from bot_handlers import start, button_handler
from localization import setup_localization

# ボットトークンを設定
TOKEN = "YOUR_BOT_TOKEN_HERE"

# ロギングの設定
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    setup_localization()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == '__main__':
    main()
```

3. `telegram_bot/bot_handlers.py`:

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ui_components import show_main_menu, show_battle_options, show_weapon_management, show_rankings, show_events, show_profile
from battle_system import start_battle, handle_battle_move
from nft_management import handle_weapon_action
from user_session import get_user_session

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_main_menu(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'start_battle':
        await start_battle(update, context)
    elif query.data in ['rock', 'paper', 'scissors']:
        await handle_battle_move(update, context)
    elif query.data == 'manage_weapons':
        await show_weapon_management(update, context)
    elif query.data.startswith('weapon_'):
        await handle_weapon_action(update, context)
    elif query.data == 'show_rankings':
        await show_rankings(update, context)
    elif query.data == 'show_events':
        await show_events(update, context)
    elif query.data == 'show_profile':
        await show_profile(update, context)
    # ... その他のコールバックハンドラ
```

4. `telegram_bot/ui_components.py`:
   このファイルには、`improved_ui.py`の内容が含まれます。

5. `utils/sui_integration.py`:

```python
from sui_sdk import SuiClient, SuiConfig

sui_config = SuiConfig.from_network('testnet')
sui_client = SuiClient(sui_config)

async def call_move_function(function_name: str, arguments: list, gas_budget: int = 1000):
    try:
        result = await sui_client.move_call(function_name, arguments, gas_budget=gas_budget)
        return result
    except Exception as e:
        # エラーハンドリング
        raise

async def query_object(object_id: str):
    try:
        result = await sui_client.get_object(object_id)
        return result
    except Exception as e:
        # エラーハンドリング
        raise

# その他のSUI関連の関数...
```

6. `README.md`:

```markdown
# SUI忍者バトル

SUI忍者バトルは、SUIブロックチェーン上で動作するTelegramボットゲームです。プレイヤーは忍者となり、NFT忍具を使って他のプレイヤーとバトルを行います。

## 特徴

- NFT忍具システム
- リアルタイムバトル
- ランキングとイベントシステム
- 多言語サポート

## セットアップ

1. リポジトリをクローン
2. 依存関係をインストール: `pip install -r requirements.txt`
3. `config.py`にTelegramボットトークンとSUI設定を追加
4. `python telegram_bot/main.py`を実行してボットを起動

## 開発

- `smart_contracts/`ディレクトリにはMoveで書かれたスマートコントラクトが含まれています。
- `telegram_bot/`ディレクトリにはPythonで書かれたTelegramボットの実装が含まれています。
- `tests/`ディレクトリにはユニットテストが含まれています。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
```

これらのファイルとプロジェクト構造を使用して、GitHubリポジトリを作成し、コードをアップロードすることができます。`.gitignore`ファイルを適切に設定し、機密情報（ボットトークンなど）がリポジトリに含まれないようにしてください。