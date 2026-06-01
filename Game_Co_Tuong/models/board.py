from __future__ import annotations

from typing import Optional

from .constants import Color, PieceType
from .game_logic import is_valid_move as rules_is_valid_move
from .piece import (
    Advisor,
    Cannon,
    Chariot,
    Elephant,
    General,
    Horse,
    Piece,
    Position,
    Soldier,
)


class Board:
    WIDTH = 9
    HEIGHT = 10

    def __init__(self) -> None:
        # grid[y][x] where x in 0..8, y in 0..9 (9 columns x 10 rows)
        self.grid: list[list[Optional[Piece]]] = []
        self.reset_board()

    def reset_board(self) -> None:
        # 10 rows x 9 cols, default None
        self.grid = [[None for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
        self.setup_initial_board()

    def setup_initial_board(self) -> None:
        """
        Standard Xiangqi (Cờ tướng) initial setup.

        Coordinate system:
        - x: 0..8 (left -> right)
        - y: 0..9 (top -> bottom)

        Black is at the top (rows 0..3), Red is at the bottom (rows 6..9).
        """
        self._place(Chariot(PieceType.CHARIOT, Color.BLACK, Position(0, 0)))
        self._place(Horse(PieceType.HORSE, Color.BLACK, Position(1, 0)))
        self._place(Elephant(PieceType.ELEPHANT, Color.BLACK, Position(2, 0)))
        self._place(Advisor(PieceType.ADVISOR, Color.BLACK, Position(3, 0)))
        self._place(General(PieceType.GENERAL, Color.BLACK, Position(4, 0)))
        self._place(Advisor(PieceType.ADVISOR, Color.BLACK, Position(5, 0)))
        self._place(Elephant(PieceType.ELEPHANT, Color.BLACK, Position(6, 0)))
        self._place(Horse(PieceType.HORSE, Color.BLACK, Position(7, 0)))
        self._place(Chariot(PieceType.CHARIOT, Color.BLACK, Position(8, 0)))

        self._place(Cannon(PieceType.CANNON, Color.BLACK, Position(1, 2)))
        self._place(Cannon(PieceType.CANNON, Color.BLACK, Position(7, 2)))

        for x in (0, 2, 4, 6, 8):
            self._place(Soldier(PieceType.SOLDIER, Color.BLACK, Position(x, 3)))

        self._place(Chariot(PieceType.CHARIOT, Color.RED, Position(0, 9)))
        self._place(Horse(PieceType.HORSE, Color.RED, Position(1, 9)))
        self._place(Elephant(PieceType.ELEPHANT, Color.RED, Position(2, 9)))
        self._place(Advisor(PieceType.ADVISOR, Color.RED, Position(3, 9)))
        self._place(General(PieceType.GENERAL, Color.RED, Position(4, 9)))
        self._place(Advisor(PieceType.ADVISOR, Color.RED, Position(5, 9)))
        self._place(Elephant(PieceType.ELEPHANT, Color.RED, Position(6, 9)))
        self._place(Horse(PieceType.HORSE, Color.RED, Position(7, 9)))
        self._place(Chariot(PieceType.CHARIOT, Color.RED, Position(8, 9)))

        self._place(Cannon(PieceType.CANNON, Color.RED, Position(1, 7)))
        self._place(Cannon(PieceType.CANNON, Color.RED, Position(7, 7)))

        for x in (0, 2, 4, 6, 8):
            self._place(Soldier(PieceType.SOLDIER, Color.RED, Position(x, 6)))

    # Backward-compatible alias (older name used previously)
    def setup_initial_position(self) -> None:
        self.setup_initial_board()

    def _place(self, piece: Piece) -> None:
        if not self.is_in_bounds(piece.position):
            raise ValueError(f"Out of bounds: {piece.position}")
        self.grid[piece.position.y][piece.position.x] = piece

    def get_piece(self, pos: Position) -> Optional[Piece]:
        return self.grid[pos.y][pos.x]

    def set_piece(self, pos: Position, piece: Optional[Piece]) -> None:
        self.grid[pos.y][pos.x] = piece
        if piece is not None:
            piece.position = pos

    def is_in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.x < self.WIDTH and 0 <= pos.y < self.HEIGHT

    def move_piece(self, from_pos: Position, to_pos: Position) -> bool:
        if not self.is_valid_move(from_pos, to_pos):
            return False

        piece = self.get_piece(from_pos)
        self.set_piece(to_pos, piece)  # also updates piece.position
        self.set_piece(from_pos, None)
        return True

    def is_valid_move(self, from_pos: Position, to_pos: Position) -> bool:
        if not self.is_in_bounds(from_pos) or not self.is_in_bounds(to_pos):
            return False
        if self.get_piece(from_pos) is None:
            return False
        if from_pos == to_pos:
            return False

        # Piece-specific rules are handled in models/game_logic.py
        return rules_is_valid_move(self, from_pos, to_pos)

    def display_board(self) -> None:
        """
        Print the board to terminal for coordinate checking.
        Uses tokens like: R_Chariot, B_General, .. for empty.
        """

        def token(p: Optional[Piece]) -> str:
            if p is None:
                return ".."
            color_prefix = "R" if p.color == Color.RED else "B"
            # PieceType is an Enum with values like "CHARIOT", "GENERAL"
            name = p.piece_type.value.title().replace("_", "")
            return f"{color_prefix}_{name}"

        # Print with y from top(0) to bottom(9) so it matches grid indices
        for y in range(self.HEIGHT):
            row = [token(self.grid[y][x]).ljust(10) for x in range(self.WIDTH)]
            print(f"{y:>2} " + " ".join(row))
        print("   " + " ".join(f"{x:^10}" for x in range(self.WIDTH)))

