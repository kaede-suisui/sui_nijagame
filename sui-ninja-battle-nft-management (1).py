# nft_management.py

from typing import List, Dict
from sui_sdk import SuiClient, SuiConfig
from user_session import get_user_session

sui_config = SuiConfig.from_network('testnet')
sui_client = SuiClient(sui_config)

class NFTManagementSystem:
    async def get_player_weapons(self, player: str) -> List[Dict]:
        weapons = await sui_client.get_objects_owned_by_address(player)
        return [self.format_weapon(weapon) for weapon in weapons if weapon.type == 'NinjaWeapon']

    def format_weapon(self, weapon: Dict) -> Dict:
        return {
            "id": weapon.id,
            "name": weapon.name,
            "type": weapon.weapon_type,
            "rarity": weapon.rarity,
            "power": weapon.power
        }

    async def create_weapon(self, player: str, weapon_type: int, rarity: int) -> Dict:
        result = await sui_client.move_call(
            'create_weapon',
            [player, weapon_type, rarity],
            gas_budget=1000
        )
        return self.format_weapon(result.created[0])

    async def upgrade_weapon(self, player: str, weapon_id: str) -> Dict:
        result = await sui_client.move_call(
            'upgrade_weapon',
            [player, weapon_id],
            gas_budget=1000
        )
        return self.format_weapon(result.modified[0])

    async def merge_weapons(self, player: str, weapon_id1: str, weapon_id2: str) -> Dict:
        result = await sui_client.move_call(
            'merge_weapons',
            [player, weapon_id1, weapon_id2],
            gas_budget=1000
        )
        return self.format_weapon(result.created[0])

nft_system = NFTManagementSystem()

# main.py での使用例
async def show_weapons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_session = await get_user_session(context, update.effective_user.id)
    weapons = await nft_system.get_player_weapons(user_session.wallet_address)
    
    if not weapons:
        await update.message.reply_text("あなたはまだ忍具を所持していません。")
        return

    keyboard = []
    for weapon in weapons:
        keyboard.append([InlineKeyboardButton(
            f"{weapon['name']} (タイプ: {weapon['type']}, レア度: {weapon['rarity']}, パワー: {weapon['power']})",
            callback_data=f"weapon_{weapon['id']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("あなたの忍具一覧:", reply_markup=reply_markup)

async def handle_weapon_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    weapon_id = query.data.split('_')[1]
    
    keyboard = [
        [InlineKeyboardButton("装備する", callback_data=f"equip_{weapon_id}")],
        [InlineKeyboardButton("強化する", callback_data=f"upgrade_{weapon_id}")],
        [InlineKeyboardButton("合成する", callback_data=f"merge_{weapon_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("忍具に対するアクションを選択してください：", reply_markup=reply_markup)

async def handle_weapon_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    action, weapon_id = query.data.split('_')
    user_session = await get_user_session(context, update.effective_user.id)

    if action == 'equip':
        user_session.selected_weapon = weapon_id
        await query.edit_message_text(f"忍具 (ID: {weapon_id}) を装備しました。")
    elif action == 'upgrade':
        upgraded_weapon = await nft_system.upgrade_weapon(user_session.wallet_address, weapon_id)
        await query.edit_message_text(f"忍具をアップグレードしました。新しいパワー: {upgraded_weapon['power']}")
    elif action == 'merge':
        context.user_data['merge_weapon'] = weapon_id
        weapons = await nft_system.get_player_weapons(user_session.wallet_address)
        keyboard = [[InlineKeyboardButton(f"{w['name']} (パワー: {w['power']})", callback_data=f"merge2_{w['id']}") 
                     for w in weapons if w['id'] != weapon_id]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("合成する2つ目の忍具を選択してください：", reply_markup=reply_markup)

async def handle_weapon_merge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    weapon_id2 = query.data.split('_')[1]
    weapon_id1 = context.user_data.pop('merge_weapon')
    user_session = await get_user_session(context, update.effective_user.id)

    merged_weapon = await nft_system.merge_weapons(user_session.wallet_address, weapon_id1, weapon_id2)
    await query.edit_message_text(f"忍具を合成しました。新しい忍具: {merged_weapon['name']} (パワー: {merged_weapon['power']})")

