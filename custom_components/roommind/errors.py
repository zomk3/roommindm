"""Errors a user can correct, translated in the UI and kept in English for the log."""

from __future__ import annotations


class RoomMindValidationError(ValueError):
    """Invalid input: *template* is the English message, the key its entry in strings.json `exceptions`.

    The panel shows the translation (component.roommind.exceptions.<key>.message) with the
    placeholders filled in, and falls back to the English text when no translation exists.
    """

    def __init__(self, translation_key: str, template: str, **placeholders: str) -> None:
        super().__init__(template.format(**placeholders))
        self.translation_key = translation_key
        self.translation_placeholders = placeholders
