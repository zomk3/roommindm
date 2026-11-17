"""Localized texts for RoomMind's push and sidebar notifications.

HA translates only entity, config and repair strings; a notification text is
built at runtime, so it picks its language from ``hass.config.language`` here.
Languages follow the frontend locales; anything else falls back to English.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant

DEFAULT_LANGUAGE = "en"

# key -> language -> (title, message); placeholders are filled with str.format
_TEXTS: dict[str, dict[str, tuple[str, str]]] = {
    "ventilate": {
        "en": (
            "RoomMind: Air the room",
            "Airing dries {room}: outdoor air holds {outdoor} g/m³ of water, indoor air {indoor} g/m³. "
            "Open a window for 5-10 minutes.",
        ),
        "de": (
            "RoomMind: Bitte lüften",
            "Lüften trocknet {room}: Die Außenluft enthält {outdoor} g/m³ Wasser, die Raumluft {indoor} g/m³. "
            "Öffne ein Fenster für 5-10 Minuten.",
        ),
        "fr": (
            "RoomMind : Aérez la pièce",
            "Aérer assèche {room} : l'air extérieur contient {outdoor} g/m³ d'eau, l'air intérieur {indoor} g/m³. "
            "Ouvrez une fenêtre pendant 5 à 10 minutes.",
        ),
        "it": (
            "RoomMind: Arieggia la stanza",
            "Arieggiare asciuga {room}: l'aria esterna contiene {outdoor} g/m³ di acqua, quella interna {indoor} g/m³. "
            "Apri una finestra per 5-10 minuti.",
        ),
    },
    "tank": {
        "en": (
            "RoomMind: Dehumidifier tank full",
            "The dehumidifier in {room} has stopped: its water tank is full.",
        ),
        "de": (
            "RoomMind: Wassertank des Luftentfeuchters voll",
            "Der Luftentfeuchter in {room} hat angehalten: Sein Wassertank ist voll.",
        ),
        "fr": (
            "RoomMind : Réservoir du déshumidificateur plein",
            "Le déshumidificateur de {room} s'est arrêté : son réservoir d'eau est plein.",
        ),
        "it": (
            "RoomMind: Serbatoio del deumidificatore pieno",
            "Il deumidificatore in {room} si è fermato: il serbatoio dell'acqua è pieno.",
        ),
    },
    "mold_risk": {
        "en": (
            "RoomMind: mold risk",
            "Mold risk in {room}: {humidity}% humidity in the room, about {surface}% at the coldest spot of the wall",
        ),
        "de": (
            "RoomMind: Schimmelgefahr",
            "Schimmelgefahr in {room}: {humidity} % Luftfeuchte im Raum, etwa {surface} % an der kältesten "
            "Stelle der Wand",
        ),
        "fr": (
            "RoomMind : risque de moisissure",
            "Risque de moisissure dans {room} : {humidity} % d'humidité dans la pièce, environ {surface} % "
            "à l'endroit le plus froid du mur",
        ),
        "it": (
            "RoomMind: rischio muffa",
            "Rischio muffa in {room}: {humidity}% di umidità nella stanza, circa {surface}% nel punto più "
            "freddo della parete",
        ),
    },
    "mold_prevention": {
        "en": (
            "RoomMind: mold prevention",
            "Mold prevention in {room}: heating target raised by {delta}",
        ),
        "de": (
            "RoomMind: Schimmelschutz",
            "Schimmelschutz in {room}: Heizziel um {delta} angehoben",
        ),
        "fr": (
            "RoomMind : prévention des moisissures",
            "Prévention des moisissures dans {room} : consigne de chauffage augmentée de {delta}",
        ),
        "it": (
            "RoomMind: prevenzione muffa",
            "Prevenzione muffa in {room}: temperatura di riscaldamento aumentata di {delta}",
        ),
    },
}


def notification_language(hass: HomeAssistant) -> str:
    """Return the supported language for HA's configured one ("de-AT" -> "de")."""
    language = getattr(hass.config, "language", None)
    if not isinstance(language, str):
        return DEFAULT_LANGUAGE
    base = language.lower().replace("_", "-").split("-")[0]
    return base if base in _TEXTS["ventilate"] else DEFAULT_LANGUAGE


def notification_text(hass: HomeAssistant, key: str, **placeholders: object) -> tuple[str, str]:
    """Return (title, message) for *key* in HA's language, placeholders filled in."""
    texts = _TEXTS[key]
    title, message = texts.get(notification_language(hass), texts[DEFAULT_LANGUAGE])
    return title, message.format(**placeholders)
