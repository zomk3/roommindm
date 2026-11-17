"""Tests for the localized notification texts."""

from unittest.mock import MagicMock

import pytest

from custom_components.roommind.utils.notification_texts import (
    _TEXTS,
    notification_language,
    notification_text,
)


def _hass(language):
    hass = MagicMock()
    hass.config.language = language
    return hass


@pytest.mark.parametrize(
    ("language", "expected"),
    [("de", "de"), ("de-AT", "de"), ("fr_CH", "fr"), ("it", "it"), ("en-GB", "en"), ("nl", "en"), (None, "en")],
)
def test_language_maps_to_supported_one(language, expected):
    assert notification_language(_hass(language)) == expected


def test_language_not_a_string_falls_back_to_english():
    assert notification_language(MagicMock()) == "en"


def test_ventilation_hint_in_german():
    title, message = notification_text(_hass("de"), "ventilate", room="Bad", outdoor="6.1", indoor="9.4")
    assert title == "RoomMind: Bitte lüften"
    assert message.startswith("Lüften trocknet Bad: Die Außenluft enthält 6.1 g/m³")
    assert "9.4 g/m³" in message


def test_unsupported_language_gets_english():
    title, message = notification_text(_hass("nl"), "tank", room="Keller")
    assert title == "RoomMind: Dehumidifier tank full"
    assert "Keller" in message


@pytest.mark.parametrize("key", list(_TEXTS))
def test_every_language_uses_the_same_placeholders(key):
    import string

    def fields(text):
        return {f for _, f, _, _ in string.Formatter().parse(text) if f}

    english = _TEXTS[key]["en"][1]
    for language, (title, message) in _TEXTS[key].items():
        assert set(_TEXTS[key]) == {"en", "de", "fr", "it"}
        assert fields(message) == fields(english), language
        assert title.startswith("RoomMind"), language
