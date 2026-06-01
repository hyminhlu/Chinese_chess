from __future__ import annotations
from models.board import Board
from models.constants import Color
from models.piece import Position

from views.game_view import GameView, ViewConfig

import pygame
import os
import sys

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, phục vụ cho việc đóng gói exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
    
def main() -> None:
    CELL_SIZE = 80
    OFFSET = 50
    board = Board()
    view = GameView(ViewConfig(cell=CELL_SIZE, margin=OFFSET))

    running = True
    selected_pos: Position | None = None
    current_turn: Color = Color.RED
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Convert pixel coordinates to board coordinates.
                # Note: row = y, col = x.
                local_x = mouse_x - OFFSET
                local_y = mouse_y - OFFSET

                col = round(local_x / CELL_SIZE)
                row = round(local_y / CELL_SIZE)

                # Bounds check: board is 9 cols (0..8) x 10 rows (0..9)
                if not (0 <= col <= 8 and 0 <= row <= 9):
                    continue

                # Optimize hit area: accept clicks within a radius around the intersection
                # so users don't need pixel-perfect aiming.
                ix = col * CELL_SIZE
                iy = row * CELL_SIZE
                r = CELL_SIZE // 2
                if (local_x - ix) * (local_x - ix) + (local_y - iy) * (local_y - iy) > r * r:
                    continue

                end_pos = Position(int(col), int(row))

                if not board.is_in_bounds(end_pos):
                    continue

                clicked_piece = board.get_piece(end_pos)

                # Click 1: select a piece of the current side.
                if selected_pos is None:
                    if clicked_piece is not None and clicked_piece.color == current_turn:
                        selected_pos = end_pos
                    continue

                # Click 2: move, re-select, or cancel selection.
                if clicked_piece is not None and clicked_piece.color == current_turn:
                    # Clicking another own piece => switch selection.
                    selected_pos = end_pos
                    continue

                if board.is_valid_move(selected_pos, end_pos):
                    board.move_piece(selected_pos, end_pos)
                    selected_pos = None
                    current_turn = Color.BLACK if current_turn == Color.RED else Color.RED
                else:
                    # Invalid move or clicking elsewhere => cancel selection.
                    selected_pos = None

        view.draw(board, selected_pos)
        view.tick(60)

    view.close()


if __name__ == "__main__":
    main()

