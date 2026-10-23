import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from mcrcon import MCRcon

# ==================== НАСТРОЙКИ БОТА И СЕРВЕРА ====================
TOKEN = "8837624302:AAEBC--oqtbsjz_X0t2kULx-nCZjLqZ_dr0"

# РАСХОДНИКИ ХОСТИНГА (Замените на IP/домен, RCON-порт и пароль от вашего сервера)
RCON_HOST = "0.0.0.0"  # Например: "193.38.15.22" или "node1.myhost.com"
RCON_PORT = 26110                           # Укажите RCON-порт, который указан в панели хостинга
RCON_PASSWORD = "trehuf4534huder143"

# Ссылки проекта
TG_CHANNEL = "https://t.me/HomePvp"
DISCORD_INVITE = "https://discord.gg/q6K7Cr6GX8"
# ====================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)

router = Router()

class DonateState(StatesGroup):
    waiting_for_nick = State()


# --- КЛАВИАТУРЫ ---

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💎 Купить привилегию", callback_data="donate_menu")],
            [InlineKeyboardButton(text="📖 Правила сервера", callback_data="rules_info")],
            [
                InlineKeyboardButton(text="📢 Telegram", url=TG_CHANNEL),
                InlineKeyboardButton(text="🎧 Discord", url=DISCORD_INVITE),
            ],
        ]
    )

def donate_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛡️ Guard — 30 ⭐", callback_data="buy_guard")],
            [InlineKeyboardButton(text="⚔️ Fooks — 50 ⭐", callback_data="buy_fooks")],
            [InlineKeyboardButton(text="👑 Mider — 100 ⭐", callback_data="buy_mider")],
            [InlineKeyboardButton(text="🟣 На главную", callback_data="back_to_main")],
        ]
    )

def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🟣 Назад в меню", callback_data="back_to_main")]
        ]
    )


# --- ОБРАБОТЧИКИ МЕНЮ ---

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "💜 **Добро пожаловать на официальный сервер Home Pvp!** 💜\n\n"
        "🔮 Здесь вы можете приобрести донат-привилегии за Telegram Stars с мгновенной и автоматической выдачей на сервер.\n\n"
        "⚡ *Выберите нужный раздел на панели управления ниже:*"
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="Markdown")

@router.callback_query(F.data == "donate_menu")
async def cb_donate(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "💎 **ЦЕНТР ДОНАТА И ПРИВИЛЕГИЙ**\n\n"
        "🔮 Выберите желаемый статус из списка ниже, чтобы ознакомиться с ценой и оформить покупку:"
    )
    await callback.message.edit_text(text, reply_markup=donate_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "rules_info")
async def cb_rules(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "📖 **ПРАВИЛА СЕРВЕРА HOME PVP**\n\n"
        "🟣 **1.** Использование читов, макросов и стороннего ПО запрещено.\n"
        "🟣 **2.** Оскорбления игроков и администрации строго наказываются.\n"
        "🟣 **3.** Попытки дюпа или багоюза ведут к вечному бану.\n\n"
        "💬 *Следите за новостями в нашем Telegram и общайтесь в Discord!*"
    )
    await callback.message.edit_text(text, reply_markup=back_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def cb_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = "💜 **Главное меню сервера Home Pvp**\n\n🔮 Выберите необходимый пункт ниже:"
    await callback.message.edit_text(text, reply_markup=main_menu(), parse_mode="Markdown")
    await callback.answer()


# --- ТЕСТОВАЯ КОМАНДА RCON ---

@router.message(Command("play"))
async def cmd_play(message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("⚠️ Формат команды: `/play [ник] [guard/fooks/mider]`", parse_mode="Markdown")
        return

    nick, rank = args[1], args[2].lower()
    if rank not in ["guard", "fooks", "mider"]:
        await message.answer("❌ Неверный ранг. Доступны: `guard`, `fooks`, `mider`", parse_mode="Markdown")
        return

    cmd = f"lp user {nick} parent add {rank}"
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT, timeout=6) as mcr:
            resp = mcr.command(cmd)
            await message.answer(f"✅ **RCON успешно отработал!**\n💬 Ответ сервера: `{resp or 'Успешно'}`", parse_mode="Markdown")
    except Exception as e:
        await message.answer(
            f"❌ **Ошибка подключения к серверу хостинга!**\n"
            f"Причина: `{e}`\n\n"
            f"💡 *Проверьте правильность IP, RCON-порта и пароля в настройках бота.*",
            parse_mode="Markdown"
        )


# --- ПРОЦЕСС ПОКУПКИ ---

@router.callback_query(F.data.in_({"buy_guard", "buy_fooks", "buy_mider"}))
async def cb_buy(callback: CallbackQuery, state: FSMContext):
    ranks = {
        "buy_guard": ("guard", "Guard", 30),
        "buy_fooks": ("fooks", "Fooks", 50),
        "buy_mider": ("mider", "Mider", 100),
    }
    key, title, cost = ranks[callback.data]
    
    await state.update_data(rank_key=key, rank_title=title, cost=cost)
    await state.set_state(DonateState.waiting_for_nick)
    
    text = (
        f"🛒 Вы выбрали покупку статуса **{title}**\n"
        f"💎 Стоимость: **{cost} Telegram Stars ⭐**\n\n"
        "✍️ **Введите ваш точный игровой ник** на сервере в ответном сообщении:"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@router.message(DonateState.waiting_for_nick)
async def process_nick(message: Message, state: FSMContext):
    nick = message.text.strip()
    if " " in nick or not (3 <= len(nick) <= 16):
        await message.answer("❌ Некорректный ник. Ник должен быть от 3 до 16 символов без пробелов. Повторите ввод:")
        return

    data = await state.get_data()
    key, title, cost = data["rank_key"], data["rank_title"], data["cost"]

    # Отправляем инвойс (payload хранит ключ ранга и ник через разделитель)
    await message.answer_invoice(
        title=f"Привилегия {title} (Home Pvp)",
        description=f"Автоматическая выдача статуса {title} для игрока {nick}",
        prices=[LabeledPrice(label=title, amount=cost)],
        payload=f"donate_{key}_{nick}",
        currency="XTR",
        provider_token="", 
    )
    await state.clear()

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


# --- УСПЕШНАЯ ОПЛАТА И АВТО-ВЫДАЧА ---

@router.message(F.successful_payment)
async def on_success_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    parts = payload.split("_")
    
    rank = parts[1] if len(parts) >= 2 else "guard"
    nick = parts[2] if len(parts) >= 3 else message.from_user.username

    rcon_cmd = f"lp user {nick} parent add {rank}"
    delivery = "❌ Ошибка выдачи через RCON"

    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT, timeout=6) as mcr:
            mcr.command(rcon_cmd)
            delivery = "✅ Успешно выдано на сервере!"
    except Exception as e:
        logging.error(f"RCON Error: {e}")

    text = (
        f"🎉 **ОПЛАТА УСПЕШНО ПРОШЛА!** 🎉\n\n"
        f"🟣 Игрок: `{nick}`\n"
        f"👑 Привилегия: **{rank.upper()}**\n"
        f"⭐ Списано: **{message.successful_payment.total_amount} XTR**\n"
        f"⚙️ Статус сервера: {delivery}\n\n"
        f"💬 *Приятной игры на Home Pvp! Если статус не появился, обратитесь в наш Discord или Telegram.*"
    )
    await message.answer(text, parse_mode="Markdown")


# --- ЗАПУСК БОТА ---

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    logging.info("Бот Home Pvp запущен и готов к работе.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())