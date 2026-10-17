from enum import IntEnum, IntFlag


class Behavior(IntEnum):
    SOLID = 1
    """Requires flag 0x1"""
    WINTER_PATH = 2
    """Requires flag 0x8 for winter-only footprints"""
    GROUND = 3
    GRAS = 4
    """Requires flag 0x20 for displaying gras"""
    GRAS_WINTER = 5
    """Requires flag 0x20 for displaying gras"""
    DARK_GRAS = 6
    """Requires flag 0x20 for displaying gras
    Requires flag 0x4 for double battles"""
    DARK_GRAS_WINTER = 7
    """Requires flag 0x20 for displaying gras
    Requires flag 0x4 for double battles"""
    LONG_GRAS = 8
    """Requires flag 0x20 for displaying gras"""
    DARK_LONG_GRAS = 9
    """Requires flag 0x20 for displaying gras
    Requires flag 0x4 for double battles"""
    CAVE_GROUND = 0xA
    """Spawns dust clouds"""
    SAND = 0xB
    DEEP_SAND = 0xC
    """Requires flag 0x8 for dark hole"""

    SNOW = 0xE
    """Requires flag 0x8 for footprints"""
    SNOW_NO_BIKE = 0xF
    """Requires flag 0x8 for footprints"""
    SLIDE = 0x10

    LAKE_BORDER = 0x12

    PUDDLE = 0x14
    RIPPLE = 0x15
    BIZARRO_HOUSE = 0x16
    BEACH_BORDER = 0x17
    ICE = 0x18
    SAND_PATH = 0x19

    PUDDLE_ENCOUNTER = 0x1C
    """Requires flag 0x4 for wild encounters"""
    STRENGTH_HOLE = 0x1D
    """Requires flag 0x1"""
    SEASONAL_FOOTPRINTS = 0x1E
    """Requires flag 0x8 for footprints"""
    GRAS_PATH = 0x1F
    """No encounters"""
    BRIDGE_SHADOW = 0x20
    """Spawns flying shadows"""
    GRAS_ALTERNATIVE = 0x21
    """Requires flag 0x20 for displaying gras"""
    # TODO


class Flags(IntFlag):
    INTERACTABLE = 0x1
    SURFABLE = 0x2
    ENCOUNTERS = 0x4
    FOOTPRINTS = 0x8
    UNKNOWN_WATER_SAND = 0x10
    GRAS_ANIMATION = 0x20
    REFLECTION = 0x40
    SHADOW = 0x80
    SHADING = 0x100
    UNKNOWN_200 = 0x200
    UNKNOWN_400 = 0x400
    UNKNOWN_800 = 0x800
    UNKNOWN_1000 = 0x1000
    UNKNOWN_2000 = 0x2000
    UNKNOWN_4000 = 0x4000
    UNKNOWN_8000 = 0x8000
