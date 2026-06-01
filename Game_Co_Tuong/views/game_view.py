from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import sys
import pygame

from models.board import Board
from models.constants import Color, PieceType
from models.piece import Piece, Position

def resource_path(*paths) -> Path:
    """
    Get absolute path to resource.
    Works in development and PyInstaller exe.
    """

    # PyInstaller extracts to _MEIPASS
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        # project root
        base_path = Path(__file__).resolve().parents[1]

    return base_path.joinpath(*paths)

@dataclass(frozen=True)
class ViewConfig:
    cell: int = 64
    margin: int = 40
    bg_color: tuple[int, int, int] = (245, 222, 179)  # wheat-like
    line_color: tuple[int, int, int] = (40, 40, 40)
    river_text_color: tuple[int, int, int] = (60, 60, 60)


class GameView:
    def __init__(self, config: ViewConfig | None = None) -> None:
        self.cfg = config or ViewConfig()

        # Board intersections: 9 columns (0..8), 10 rows (0..9)
        self.board_px_w = self.cfg.cell * (Board.WIDTH - 1)
        self.board_px_h = self.cfg.cell * (Board.HEIGHT - 1)
        self.window_w = self.board_px_w + self.cfg.margin * 2
        self.window_h = self.board_px_h + self.cfg.margin * 2

        pygame.init()
        pygame.display.set_caption("Cờ Tướng (Xiangqi) - Pygame")
        self.screen = pygame.display.set_mode((self.window_w, self.window_h))
        self.clock = pygame.time.Clock()

        self.font_piece = pygame.font.SysFont("arial", 18, bold=True)
        self.font_river = pygame.font.SysFont("arial", 20, bold=True)

        # Load piece images (optional; fallback to drawn circles if missing)
        self.piece_images: dict[tuple[Color, PieceType], pygame.Surface] = {}
        self._load_piece_images()

        # Subtle board-lines overlay surface so pieces don't hide lines
        self._grid_overlay: pygame.Surface | None = None

   def _load_piece_images(self) -> None:
        # assets/images/pieces/red
        # assets/images/pieces/black
        pieces_dir = resource_path("assets", "images", "pieces")

        # Piece size
        target_px = int(self.cfg.cell * 0.8)

        if target_px <= 0:
            return

    def candidates(color: Color, piece_type: PieceType) -> list[Path]:

        sub = "red" if color == Color.RED else "black"

        pt = piece_type.value.lower()

        piece_folder = pieces_dir / sub

        return [
            piece_folder / f"{pt}.png",
            piece_folder / f"{pt}.webp",
            piece_folder / f"{pt}.jpg",
            piece_folder / f"{pt}.jpeg",
        ]

    for color in (Color.RED, Color.BLACK):

        for piece_type in (
            PieceType.GENERAL,
            PieceType.ADVISOR,
            PieceType.ELEPHANT,
            PieceType.HORSE,
            PieceType.CHARIOT,
            PieceType.CANNON,
            PieceType.SOLDIER,
        ):

            surf = None

            for path in candidates(color, piece_type):

                try:

                    if not path.exists():
                        continue

                    loaded = pygame.image.load(
                        str(path)
                    ).convert_alpha()

                    w, h = loaded.get_size()

                    if w <= 0 or h <= 0:
                        continue

                    scale = min(
                        target_px / w,
                        target_px / h
                    )

                    new_size = (
                        max(1, int(w * scale)),
                        max(1, int(h * scale))
                    )

                    surf = pygame.transform.smoothscale(
                        loaded,
                        new_size
                    )

                    print(f"[OK] Loaded piece: {path}")

                    break

                except Exception as e:

                    print(f"[ERROR] Failed loading {path}")
                    print(e)

            if surf is not None:

                self.piece_images[(color, piece_type)] = surf

            else:

                print(
                    f"[MISSING] {color.value} {piece_type.value}"
                )
    def board_to_screen(self, pos: Position) -> tuple[int, int]:
        x = self.cfg.margin + pos.x * self.cfg.cell
        y = self.cfg.margin + pos.y * self.cfg.cell
        return x, y

    def draw(self, board: Board, selected_pos: Position | None = None) -> None:
        self.screen.fill(self.cfg.bg_color)
        self._draw_board_lines()
        self._draw_palaces()
        self._draw_river_label()
        self._draw_pieces(board)
        self._draw_board_lines_overlay()
        self._draw_selection_highlight(selected_pos)
        pygame.display.flip()

    def _draw_selection_highlight(self, selected_pos: Position | None) -> None:
        if selected_pos is None:
            return

        # Draw an outline rectangle around the selected position.
        cx, cy = self.board_to_screen(selected_pos)
        size = self.cfg.cell
        rect = pygame.Rect(cx - size // 2, cy - size // 2, size, size)
        pygame.draw.rect(self.screen, (255, 215, 0), rect, 3)

    def _draw_board_lines_overlay(self) -> None:
        """
        Draw a semi-transparent copy of the grid above pieces so
        the intersections/lines remain visible.
        """
        if self._grid_overlay is None or self._grid_overlay.get_size() != (
            self.window_w,
            self.window_h,
        ):
            self._grid_overlay = pygame.Surface(
                (self.window_w, self.window_h), flags=pygame.SRCALPHA
            )

        overlay = self._grid_overlay
        overlay.fill((0, 0, 0, 0))
        line = (*self.cfg.line_color, 90)  # RGBA

        for y in range(Board.HEIGHT):
            start = self.board_to_screen(Position(0, y))
            end = self.board_to_screen(Position(Board.WIDTH - 1, y))
            pygame.draw.line(overlay, line, start, end, 1)

        for x in range(Board.WIDTH):
            if x in (0, Board.WIDTH - 1):
                start = self.board_to_screen(Position(x, 0))
                end = self.board_to_screen(Position(x, Board.HEIGHT - 1))
                pygame.draw.line(overlay, line, start, end, 1)
            else:
                start1 = self.board_to_screen(Position(x, 0))
                end1 = self.board_to_screen(Position(x, 4))
                start2 = self.board_to_screen(Position(x, 5))
                end2 = self.board_to_screen(Position(x, Board.HEIGHT - 1))
                pygame.draw.line(overlay, line, start1, end1, 1)
                pygame.draw.line(overlay, line, start2, end2, 1)

        self.screen.blit(overlay, (0, 0))

    def _draw_board_lines(self) -> None:
        # Horizontal lines (y = 0..9)
        for y in range(Board.HEIGHT):
            start = self.board_to_screen(Position(0, y))
            end = self.board_to_screen(Position(Board.WIDTH - 1, y))
            pygame.draw.line(self.screen, self.cfg.line_color, start, end, 2)

        # Vertical lines (x = 0..8), with river gap for x=1..7
        for x in range(Board.WIDTH):
            if x in (0, Board.WIDTH - 1):
                start = self.board_to_screen(Position(x, 0))
                end = self.board_to_screen(Position(x, Board.HEIGHT - 1))
                pygame.draw.line(self.screen, self.cfg.line_color, start, end, 2)
            else:
                start1 = self.board_to_screen(Position(x, 0))
                end1 = self.board_to_screen(Position(x, 4))
                start2 = self.board_to_screen(Position(x, 5))
                end2 = self.board_to_screen(Position(x, Board.HEIGHT - 1))
                pygame.draw.line(self.screen, self.cfg.line_color, start1, end1, 2)
                pygame.draw.line(self.screen, self.cfg.line_color, start2, end2, 2)

        # Intersection dots are optional; keep clean for now

    def _draw_palaces(self) -> None:
        # Palace diagonals:
        # Top palace: columns 3..5, rows 0..2
        self._draw_diag(Position(3, 0), Position(5, 2))
        self._draw_diag(Position(5, 0), Position(3, 2))

        # Bottom palace: columns 3..5, rows 7..9
        self._draw_diag(Position(3, 7), Position(5, 9))
        self._draw_diag(Position(5, 7), Position(3, 9))

    def _draw_diag(self, a: Position, b: Position) -> None:
        pygame.draw.line(
            self.screen,
            self.cfg.line_color,
            self.board_to_screen(a),
            self.board_to_screen(b),
            2,
        )

    def _draw_river_label(self) -> None:
        # Render a subtle "river" label in the gap area
        y_river = self.cfg.margin + 4.5 * self.cfg.cell
        text_left = self.font_river.render("SÔNG", True, self.cfg.river_text_color)
        text_right = self.font_river.render("SÔNG", True, self.cfg.river_text_color)

        x_left = self.cfg.margin + self.board_px_w * 0.25 - text_left.get_width() / 2
        x_right = self.cfg.margin + self.board_px_w * 0.75 - text_right.get_width() / 2

        self.screen.blit(text_left, (x_left, y_river - text_left.get_height() / 2))
        self.screen.blit(text_right, (x_right, y_river - text_right.get_height() / 2))

    def _draw_pieces(self, board: Board) -> None:
        radius = int(self.cfg.cell * 0.36)
        for y in range(Board.HEIGHT):
            for x in range(Board.WIDTH):
                piece = board.grid[y][x]
                if piece is None:
                    continue

                cx, cy = self.board_to_screen(Position(x, y))
                self.draw_piece(piece, cx, cy, radius)

    def draw_piece(self, piece: Piece, x: int, y: int, radius: int) -> None:
        """
        Draw a piece using images from assets if available.
        Fallback to a simple drawn circle if the image is missing.
        """
        img = self.piece_images.get((piece.color, piece.piece_type))
        if img is None:
            self._draw_piece_fallback(piece, x, y, radius)
            return

        rect = img.get_rect(center=(x, y))
        self.screen.blit(img, rect)

    def _draw_piece_fallback(self, piece: Piece, x: int, y: int, radius: int) -> None:
        # Colors requested by user
        cream = (245, 245, 220)  # #F5F5DC
        wood_brown = (139, 69, 19)  # #8B4513
        red_text = (200, 0, 0)
        black_text = (0, 0, 0)

        pygame.draw.circle(self.screen, cream, (x, y), radius)
        pygame.draw.circle(self.screen, wood_brown, (x, y), radius, 4)
        pygame.draw.circle(self.screen, wood_brown, (x, y), max(2, radius - 10), 2)

        label_map: dict[PieceType, str] = {
            PieceType.CHARIOT: "Xe",
            PieceType.HORSE: "Mã",
            PieceType.CANNON: "Pháo",
            PieceType.GENERAL: "Tướng",
            PieceType.ADVISOR: "Sĩ",
            PieceType.ELEPHANT: "Tượng",
            PieceType.SOLDIER: "Tốt",
        }
        label = label_map.get(piece.piece_type, "?")
        color = red_text if piece.color == Color.RED else black_text

        text = self.font_piece.render(label, True, color)
        self.screen.blit(text, (x - text.get_width() / 2, y - text.get_height() / 2))

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
        return True

    def tick(self, fps: int = 60) -> None:
        self.clock.tick(fps)

    def close(self) -> None:
        pygame.quit()

