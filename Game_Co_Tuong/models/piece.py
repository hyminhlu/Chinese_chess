from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .constants import Color, PieceType

if TYPE_CHECKING:
    from .board import Board


@dataclass(frozen=True)
class Position:
    x: int  # 0..8 (file)
    y: int  # 0..9 (rank)


@dataclass
class Piece:
    piece_type: PieceType
    color: Color
    position: Position

    def get_valid_moves(self, board: Board) -> list[Position]:
        return []


class General(Piece):
    def get_valid_moves(self, board: Board) -> list[Position]:
        return []


class Advisor(Piece):
    def get_valid_moves(self, board: Board) -> list[Position]:
        return []


class Elephant(Piece):
    def get_valid_moves(self, board: Board) -> list[Position]:
        return []


class Horse(Piece):
    def get_valid_moves(self, board: Board) -> list[Position]:
        return []


class Chariot(Piece):
    def get_valid_moves(self, board: Board) -> list[Position]:
        return []


class Cannon(Piece):
    def get_valid_moves(self, board: Board) -> list[Position]:
        return []


class Soldier(Piece):
    def get_valid_moves(self, board: Board) -> list[Position]:
        return []

