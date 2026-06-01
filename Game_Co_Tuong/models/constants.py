from __future__ import annotations

from enum import Enum


class PieceType(str, Enum):
    GENERAL = "GENERAL"   # Tướng
    ADVISOR = "ADVISOR"   # Sĩ
    ELEPHANT = "ELEPHANT" # Tượng
    HORSE = "HORSE"       # Mã
    CHARIOT = "CHARIOT"   # Xe
    CANNON = "CANNON"     # Pháo
    SOLDIER = "SOLDIER"   # Tốt


class Color(str, Enum):
    RED = "RED"
    BLACK = "BLACK"

