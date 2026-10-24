from typing import TYPE_CHECKING
from dataclasses import dataclass

from ...ndspy.narc import NARC
from . import Zone, Area, Container

if TYPE_CHECKING:
    from ...ndspy.rom import NintendoDSRom


class MatrixEdit(dict[tuple[int, int, bool], int]):
    matrix: int

    def __init__(self, o, matrix=-1):
        super().__init__(o)
        self.matrix = matrix


def insert_new_zone(dest: "NintendoDSRom", source: "NintendoDSRom", zone_id: int, *, matrix: MatrixEdit | None = None):
    zones = NARC(source.getFileByName("a/0/1/2")).files[0]
    zone = Zone.from_bytes(zones, zone_id)
    ...
