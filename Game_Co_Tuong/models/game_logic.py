from __future__ import annotations

from models.constants import Color, PieceType
from models.piece import Position


def _find_general(board, color: Color) -> Position | None:
    for y in range(len(board.grid)):
        for x in range(len(board.grid[y])):
            p = board.grid[y][x]
            if p is not None and p.piece_type == PieceType.GENERAL and p.color == color:
                return Position(x, y)
    return None


def is_exposed_general(board) -> bool:
    """
    Return True if the two generals are facing each other directly
    on the same column with no pieces between them.
    """
    red_g = _find_general(board, Color.RED)
    black_g = _find_general(board, Color.BLACK)
    if red_g is None or black_g is None:
        return False

    if red_g.x != black_g.x:
        return False

    x = red_g.x
    y1, y2 = sorted([red_g.y, black_g.y])
    for y in range(y1 + 1, y2):
        if board.grid[y][x] is not None:
            return False
    return True


def is_valid_rook_move(board, start_pos: Position, end_pos: Position) -> bool:
    """
    Validate Xiangqi rook (Xe / Chariot) move.

    Rules implemented:
    - Must move in straight line (same row or same column)
    - Path between start and end must be empty (no blocking pieces)
    - Destination can be empty or contain opponent; cannot capture own piece
    """
    start_piece = board.get_piece(start_pos)
    if start_piece is None:
        return False

    # Direction constraint
    if start_pos.y != end_pos.y and start_pos.x != end_pos.x:
        return False

    dest_piece = board.get_piece(end_pos)
    if dest_piece is not None and dest_piece.color == start_piece.color:
        return False

    # Blocking check
    dx = 0 if start_pos.x == end_pos.x else (1 if end_pos.x > start_pos.x else -1)
    dy = 0 if start_pos.y == end_pos.y else (1 if end_pos.y > start_pos.y else -1)

    x = start_pos.x + dx
    y = start_pos.y + dy
    while (x, y) != (end_pos.x, end_pos.y):
        if board.grid[y][x] is not None:
            return False
        x += dx
        y += dy

    return True


def is_valid_general_move(board, start_pos: Position, end_pos: Position, is_red: bool) -> bool:
    """
    Validate Xiangqi general (Tướng / General) move.

    Rules implemented:
    - Must move exactly 1 step orthogonally (Manhattan distance 1)
    - Must stay inside the palace:
      - columns 3..5
      - Red rows 7..9, Black rows 0..2
    """
    if abs(start_pos.y - end_pos.y) + abs(start_pos.x - end_pos.x) != 1:
        return False

    if not (3 <= end_pos.x <= 5):
        return False

    if is_red:
        return 7 <= end_pos.y <= 9
    return 0 <= end_pos.y <= 2


def is_valid_elephant_move(
    board, start_pos: Position, end_pos: Position, is_red: bool
) -> bool:
    """
    Validate Xiangqi elephant (Tượng / Elephant) move.

    Rules implemented:
    - Must move exactly 2 steps diagonally
    - "Elephant eye" (the midpoint square) must be empty
    - Cannot cross the river:
      - Red: end_row >= 5
      - Black: end_row <= 4
    """
    # Must move 2 diagonally
    if abs(start_pos.x - end_pos.x) != 2 or abs(start_pos.y - end_pos.y) != 2:
        return False

    # Elephant eye (midpoint) must be empty
    mid_x = (start_pos.x + end_pos.x) // 2
    mid_y = (start_pos.y + end_pos.y) // 2
    if board.grid[mid_y][mid_x] is not None:
        return False

    # River boundary constraint
    if is_red:
        return end_pos.y >= 5
    return end_pos.y <= 4


def is_valid_advisor_move(board, start_pos: Position, end_pos: Position, is_red: bool) -> bool:
    """
    Validate Xiangqi advisor (Sĩ / Advisor) move.

    Rules implemented:
    - Must move exactly 1 step diagonally
    - Must stay inside the palace:
      - columns 3..5
      - Red rows 7..9, Black rows 0..2
    """
    if abs(start_pos.x - end_pos.x) != 1 or abs(start_pos.y - end_pos.y) != 1:
        return False

    if not (3 <= end_pos.x <= 5):
        return False

    if is_red:
        return 7 <= end_pos.y <= 9
    return 0 <= end_pos.y <= 2


def is_valid_horse_move(board, start_pos: Position, end_pos: Position) -> bool:
    """
    Validate Xiangqi horse (Mã / Horse) move.

    Rules implemented:
    - Must move in an L-shape: (2,1) or (1,2)
    - "Horse leg" square must be empty:
      - If moving primarily vertically (diff_row == 2): leg is midpoint row, same start col
      - If moving primarily horizontally (diff_col == 2): leg is same start row, midpoint col
    - Destination is handled by the central dispatcher (cannot capture own piece).
    """
    diff_row = abs(start_pos.y - end_pos.y)
    diff_col = abs(start_pos.x - end_pos.x)

    if not ((diff_row == 2 and diff_col == 1) or (diff_row == 1 and diff_col == 2)):
        return False

    if diff_row == 2:
        leg_y = (start_pos.y + end_pos.y) // 2
        leg_x = start_pos.x
    else:
        leg_y = start_pos.y
        leg_x = (start_pos.x + end_pos.x) // 2

    if board.grid[leg_y][leg_x] is not None:
        return False

    return True


def is_valid_cannon_move(board, start_pos: Position, end_pos: Position) -> bool:
    """
    Validate Xiangqi cannon (Pháo / Cannon) move.

    Rules implemented:
    - Must move in straight line (same row or same column)
    - Count pieces strictly between start and end (blockers)
    - If destination is empty: blockers must be 0
    - If destination has opponent: blockers must be exactly 1 (the "screen"/ngòi)
    - If destination has own piece: invalid
    """
    start_piece = board.get_piece(start_pos)
    if start_piece is None:
        return False

    # Direction constraint
    if start_pos.y != end_pos.y and start_pos.x != end_pos.x:
        return False

    dest_piece = board.get_piece(end_pos)
    if dest_piece is not None and dest_piece.color == start_piece.color:
        return False

    dx = 0 if start_pos.x == end_pos.x else (1 if end_pos.x > start_pos.x else -1)
    dy = 0 if start_pos.y == end_pos.y else (1 if end_pos.y > start_pos.y else -1)

    blockers = 0
    x = start_pos.x + dx
    y = start_pos.y + dy
    while (x, y) != (end_pos.x, end_pos.y):
        if board.grid[y][x] is not None:
            blockers += 1
        x += dx
        y += dy

    if dest_piece is None:
        return blockers == 0

    # Capture: must have exactly one screen piece between
    return blockers == 1


def is_valid_soldier_move(board, start_pos: Position, end_pos: Position, is_red: bool) -> bool:
    """
    Validate Xiangqi soldier (Tốt / Soldier) move.

    Rules implemented:
    - Must move exactly 1 step orthogonally (Manhattan distance 1)
    - Red moves "up" (decreasing row/y), Black moves "down" (increasing row/y)
    - Before crossing the river: can only move forward (no sideways)
    - After crossing the river: can move forward or sideways
    - Never allowed to move backward
    """
    start_row, start_col = start_pos.y, start_pos.x
    end_row, end_col = end_pos.y, end_pos.x

    # Must move exactly 1 step (Manhattan distance 1)
    if abs(start_row - end_row) + abs(start_col - end_col) != 1:
        return False

    if is_red:
        # Never move backward (red cannot increase row)
        if end_row > start_row:
            return False

        # Not crossed river yet: start_row >= 5 -> only forward 1
        if start_row >= 5:
            return start_col == end_col and (start_row - end_row) == 1

        # Crossed river: start_row < 5 -> forward 1 or sideways 1
        return abs(start_col - end_col) + (start_row - end_row) == 1

    # Black
    # Never move backward (black cannot decrease row)
    if end_row < start_row:
        return False

    # Not crossed river yet: start_row <= 4 -> only forward 1
    if start_row <= 4:
        return start_col == end_col and (end_row - start_row) == 1

    # Crossed river: start_row > 4 -> forward 1 or sideways 1
    return abs(start_col - end_col) + (end_row - start_row) == 1


def is_in_check(board, color: Color) -> bool:
    """
    True if the general of `color` is currently attackable
    by any opponent piece under the implemented movement rules.
    """
    gpos = _find_general(board, color)
    if gpos is None:
        return False

    enemy = Color.BLACK if color == Color.RED else Color.RED

    def attacks(piece, start: Position, target: Position) -> bool:
        pt = piece.piece_type
        if pt == PieceType.CHARIOT:
            return is_valid_rook_move(board, start, target)
        if pt == PieceType.CANNON:
            # Cannon only "attacks" by capture rule, which is exactly what we need for check.
            return is_valid_cannon_move(board, start, target)
        if pt == PieceType.HORSE:
            return is_valid_horse_move(board, start, target)
        if pt == PieceType.ELEPHANT:
            return is_valid_elephant_move(board, start, target, is_red=(piece.color == Color.RED))
        if pt == PieceType.ADVISOR:
            return is_valid_advisor_move(board, start, target, is_red=(piece.color == Color.RED))
        if pt == PieceType.SOLDIER:
            return is_valid_soldier_move(board, start, target, is_red=(piece.color == Color.RED))
        if pt == PieceType.GENERAL:
            return is_valid_general_move(board, start, target, is_red=(piece.color == Color.RED))
        return False

    for y in range(len(board.grid)):
        for x in range(len(board.grid[y])):
            p = board.grid[y][x]
            if p is None or p.color != enemy:
                continue
            if attacks(p, Position(x, y), gpos):
                return True

    return False


def is_valid_move(board, start_pos: Position, end_pos: Position) -> bool:
    """
    Central dispatcher for move validation.
    Currently implements rook/chariot logic; others are permissive placeholders.
    """
    piece = board.get_piece(start_pos)
    if piece is None:
        return False

    # Basic same-color destination check (applies to all pieces)
    dest = board.get_piece(end_pos)
    if dest is not None and dest.color == piece.color:
        return False

    if piece.piece_type == PieceType.CHARIOT:
        ok = is_valid_rook_move(board, start_pos, end_pos)
    elif piece.piece_type == PieceType.GENERAL:
        ok = is_valid_general_move(
            board, start_pos, end_pos, is_red=(piece.color == Color.RED)
        )
    elif piece.piece_type == PieceType.ADVISOR:
        ok = is_valid_advisor_move(
            board, start_pos, end_pos, is_red=(piece.color == Color.RED)
        )
    elif piece.piece_type == PieceType.HORSE:
        ok = is_valid_horse_move(board, start_pos, end_pos)
    elif piece.piece_type == PieceType.ELEPHANT:
        ok = is_valid_elephant_move(
            board, start_pos, end_pos, is_red=(piece.color == Color.RED)
        )
    elif piece.piece_type == PieceType.CANNON:
        ok = is_valid_cannon_move(board, start_pos, end_pos)
    elif piece.piece_type == PieceType.SOLDIER:
        ok = is_valid_soldier_move(
            board, start_pos, end_pos, is_red=(piece.color == Color.RED)
        )
    else:
        # TODO: Implement rules for other pieces
        ok = True

    if not ok:
        return False

    # Global rule: a move is invalid if it causes the two generals to face each other.
    moving_piece = board.get_piece(start_pos)
    captured_piece = board.get_piece(end_pos)
    if moving_piece is None:
        return False

    old_pos = moving_piece.position
    board.set_piece(end_pos, moving_piece)
    board.set_piece(start_pos, None)
    exposed = is_exposed_general(board)
    in_check = is_in_check(board, moving_piece.color)
    # revert
    board.set_piece(start_pos, moving_piece)
    board.set_piece(end_pos, captured_piece)
    moving_piece.position = old_pos

    if exposed:
        return False
    if in_check:
        return False

    return True

