"""Offline checks; never contact Telegram or use the real bot token."""

import importlib
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest
import requests

import data


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setitem(sys.modules, "token_api", SimpleNamespace(token="123456:test-token"))
    sys.modules.pop("main", None)
    module = importlib.import_module("main")
    monkeypatch.setattr(module, "bot", Mock())
    return module


@pytest.fixture
def frame():
    return pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-10-15", "2026-10-17"]).tz_localize("Asia/Tehran"),
        "date_jalali": ["1405/07/23", "1405/07/25"],
        "price": [267400.0, 264097.5],
    })


def test_start_shows_two_buttons(app):
    app.welcome(SimpleNamespace(chat=SimpleNamespace(id=42)))
    keyboard = app.bot.send_message.call_args.kwargs["reply_markup"].keyboard
    assert [[button["text"] for button in row] for row in keyboard] == [
        [app.USD_BUTTON], [app.EUR_BUTTON]
    ]


@pytest.mark.parametrize("currency,name", [("USD", "دلار"), ("EUR", "یورو")])
def test_selected_currency_sends_png(app, monkeypatch, frame, currency, name):
    fetch = Mock(return_value=frame)
    monkeypatch.setattr(app, "get_history", fetch)
    button = app.USD_BUTTON if currency == "USD" else app.EUR_BUTTON
    def inspect_photo(chat_id, image, **kwargs):
        assert chat_id == 42
        assert image.read(8) == b"\x89PNG\r\n\x1a\n"
        assert name in kwargs["caption"]
        assert "1405/07/25" in kwargs["caption"]
    app.bot.send_photo.side_effect = inspect_photo
    app.send_chart(SimpleNamespace(chat=SimpleNamespace(id=42), text=button))
    fetch.assert_called_once_with(currency)
    app.bot.send_photo.assert_called_once()
    assert app.bot.send_photo.call_args.args[1].closed


def test_network_error_shows_retry_message(app, monkeypatch):
    monkeypatch.setattr(app, "get_history", Mock(side_effect=requests.Timeout()))
    app.send_chart(SimpleNamespace(chat=SimpleNamespace(id=42), text=app.USD_BUTTON))
    app.bot.send_photo.assert_not_called()
    assert "دوباره" in app.bot.send_message.call_args.args[1]


def test_other_text_shows_menu(app):
    app.unknown_message(SimpleNamespace(chat=SimpleNamespace(id=42)))
    assert "reply_markup" in app.bot.send_message.call_args.kwargs


@pytest.mark.parametrize("currency", ["USD", "EUR"])
def test_history_filters_calendar_months_and_sorts(monkeypatch, currency):
    rows = [
        {"t_tehran": date + "T00:00:00+03:30", "date_jalali": date, "high": 120, "low": 100}
        for date in ["2026-10-18", "2026-10-17", "2026-07-16", "2026-07-17"]
    ]
    response = Mock()
    response.json.return_value = {"meta": {"unit": "toman"}, "data": rows}
    fetch = Mock(return_value=response)
    monkeypatch.setattr(data.requests, "get", fetch)
    result = data.get_history(currency, pd.Timestamp("2026-10-17"))
    assert result["date_jalali"].tolist() == ["2026-07-17", "2026-10-17"]
    assert result["price"].tolist() == [110, 110]
    assert f"/{currency}_IRR_FREE.json" in fetch.call_args.args[0]
    response.raise_for_status.assert_called_once()


def test_history_rejects_empty_data(monkeypatch):
    response = Mock()
    response.json.return_value = {"meta": {"unit": "toman"}, "data": []}
    monkeypatch.setattr(data.requests, "get", Mock(return_value=response))
    with pytest.raises(ValueError, match="No price history"):
        data.get_history("USD")
