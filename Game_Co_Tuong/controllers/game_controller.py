from __future__ import annotations

from dataclasses import dataclass

from models.board import Board, Position


@dataclass
class MoveResult:
    success: bool
    message: str = ""


class GameController:
    def __init__(self, board: Board) -> None:
        self.board = board

    def try_move(self, from_pos: Position, to_pos: Position) -> MoveResult:
        ok = self.board.move_piece(from_pos, to_pos)
        return MoveResult(success=ok, message="" if ok else "Invalid move")

