from .classification import *
from .. import ItemData

special: dict[str, ItemData] = {
    "Running Shoes": ItemData(0x85, always_useful),  # Not implemented yet
    "Out of logic": ItemData(1000000, always_progression),
}
