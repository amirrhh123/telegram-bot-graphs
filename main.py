"""Telegram menu for dollar and euro price charts."""

import logging
from io import BytesIO
from threading import Lock

import pandas as pd
import requests
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import StrMethodFormatter
from telebot import TeleBot, types

from data import get_history
from token_api import token

USD_BUTTON = "نمودار 3 ماه اخیر دلار"
EUR_BUTTON = "نمودار 3 ماه اخیر یورو"
CURRENCIES = {USD_BUTTON: ("USD", "دلار"), EUR_BUTTON: ("EUR", "یورو")}
chart_lock = Lock()
logger = logging.getLogger(__name__)
bot = TeleBot(token)


def menu() -> types.ReplyKeyboardMarkup:
    """Build the two currency buttons."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(types.KeyboardButton(USD_BUTTON), types.KeyboardButton(EUR_BUTTON))
    return keyboard


def render_chart(frame: pd.DataFrame, currency: str) -> BytesIO:
    """Render a PNG without opening a desktop window."""
    with chart_lock:
        figure = Figure(figsize=(12, 5), layout="constrained")
        FigureCanvasAgg(figure)
        ax = figure.subplots()
        try:
            dates = frame["timestamp"].dt.tz_localize(None)
            ax.plot(dates, frame["price"], color="#2166ac", linewidth=2)
            # Use real dates for spacing and Jalali text for the labels.
            step = max(1, (len(frame) + 7) // 8)
            positions = sorted(set(range(0, len(frame), step)) | {len(frame) - 1})
            ax.set_xticks(dates.iloc[positions])
            ax.set_xticklabels(frame["date_jalali"].iloc[positions], rotation=35, ha="right")
            ax.set_title(f"{currency} - Last 3 months")
            ax.set_xlabel("Date (Jalali)")
            ax.set_ylabel("Daily high/low midpoint (Toman)")
            ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
            ax.grid(alpha=0.25)
            image = BytesIO()
            image.name = f"{currency.lower()}_3months.png"
            figure.savefig(image, format="png", dpi=140)
            image.seek(0)
            return image
        finally:
            figure.clear()


@bot.message_handler(commands=["start"])
def welcome(message: types.Message) -> None:
    """Show the chart menu after /start."""
    bot.send_message(
        message.chat.id,
        "سلام! نمودار کدوم ارز رو می‌خوای ببینی؟",
        reply_markup=menu(),
    )


@bot.message_handler(func=lambda message: message.text in CURRENCIES)
def send_chart(message: types.Message) -> None:
    """Fetch the selected currency and send its chart."""
    currency, name = CURRENCIES[message.text]
    bot.send_chat_action(message.chat.id, "upload_photo")
    try:
        frame = get_history(currency)
        image = render_chart(frame, currency)
    except (requests.RequestException, ValueError, KeyError, TypeError):
        logger.exception("Could not prepare %s chart", currency)
        bot.send_message(
            message.chat.id,
            "دریافت نمودار فعلاً ممکن نیست. لطفاً کمی بعد دوباره امتحان کن.",
            reply_markup=menu(),
        )
        return
    with image:
        bot.send_photo(
            message.chat.id,
            image,
            caption=(
                f"نمودار ۳ ماه اخیر {name}\n"
                f"داده‌های موجود: {frame.iloc[0]['date_jalali']} تا "
                f"{frame.iloc[-1]['date_jalali']}\n"
                "واحد: تومان | قیمت هر روز: میانگین سقف و کف روز"
            ),
            reply_markup=menu(),
        )


@bot.message_handler(content_types=["text"])
def unknown_message(message: types.Message) -> None:
    """Guide other text messages back to the menu."""
    bot.send_message(message.chat.id, "یکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=menu())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot.infinity_polling(timeout=50)
