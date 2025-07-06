"""Game constants and default configurations for Dōbutsu Shōgi."""

from .core import ColIndex, PieceId, PieceState, PieceType, Player, RowIndex

# Default initial board setup
DEFAULT_INITIAL_SETUP: list[PieceState] = [
    # Sente (bottom player) - Row 1
    PieceState(
        piece_id=PieceId(0),
        piece_type=PieceType.ELEPHANT,
        piece_owner=Player.SENTE.value,
        row=RowIndex(1),
        col=ColIndex(1),
    ),
    PieceState(
        piece_id=PieceId(1),
        piece_type=PieceType.LION,
        piece_owner=Player.SENTE.value,
        row=RowIndex(1),
        col=ColIndex(2),
    ),
    PieceState(
        piece_id=PieceId(2),
        piece_type=PieceType.GIRAFFE,
        piece_owner=Player.SENTE.value,
        row=RowIndex(1),
        col=ColIndex(3),
    ),
    PieceState(
        piece_id=PieceId(3),
        piece_type=PieceType.CHICK,
        piece_owner=Player.SENTE.value,
        row=RowIndex(2),
        col=ColIndex(2),
    ),
    # Gote (top player) - Row 4
    PieceState(
        piece_id=PieceId(4),
        piece_type=PieceType.GIRAFFE,
        piece_owner=Player.GOTE.value,
        row=RowIndex(4),
        col=ColIndex(1),
    ),
    PieceState(
        piece_id=PieceId(5),
        piece_type=PieceType.LION,
        piece_owner=Player.GOTE.value,
        row=RowIndex(4),
        col=ColIndex(2),
    ),
    PieceState(
        piece_id=PieceId(6),
        piece_type=PieceType.ELEPHANT,
        piece_owner=Player.GOTE.value,
        row=RowIndex(4),
        col=ColIndex(3),
    ),
    PieceState(
        piece_id=PieceId(7),
        piece_type=PieceType.CHICK,
        piece_owner=Player.GOTE.value,
        row=RowIndex(3),
        col=ColIndex(2),
    ),
]
