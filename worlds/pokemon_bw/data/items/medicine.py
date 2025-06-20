from .. import ItemData
from .classification import *

item_table: dict[str, ItemData] = {
    "Potion": ItemData(0x0011, always_filler, "Medicine"),
    "Antidote": ItemData(0x0012, always_filler, "Medicine"),
    "Burn Heal": ItemData(0x0013, always_filler, "Medicine"),
    "Ice Heal": ItemData(0x0014, always_filler, "Medicine"),
    "Awakening": ItemData(0x0015, always_filler, "Medicine"),
    "Parlyz Heal": ItemData(0x0016, always_filler, "Medicine"),
    "Full Restore": ItemData(0x0017, always_filler, "Medicine"),
    "Max Potion": ItemData(0x0018, always_filler, "Medicine"),
    "Hyper Potion": ItemData(0x0019, always_filler, "Medicine"),
    "Super Potion": ItemData(0x001A, always_filler, "Medicine"),
    "Full Heal": ItemData(0x001B, always_filler, "Medicine"),
    "Revive": ItemData(0x001C, always_filler, "Medicine"),
    "Max Revive": ItemData(0x001D, always_filler, "Medicine"),
    "Fresh Water": ItemData(0x001E, always_filler, "Medicine"),
    "Soda Pop": ItemData(0x001F, always_filler, "Medicine"),
    "Lemonade": ItemData(0x0020, always_filler, "Medicine"),
    "Moomoo Milk": ItemData(0x0021, always_filler, "Medicine"),
    "Energy Powder": ItemData(0x0022, always_filler, "Medicine"),
    "Energy Root": ItemData(0x0023, always_filler, "Medicine"),
    "Heal Powder": ItemData(0x0024, always_filler, "Medicine"),
    "Revival Herb": ItemData(0x0025, always_filler, "Medicine"),
    "Ether": ItemData(0x0026, always_filler, "Medicine"),
    "Max Ether": ItemData(0x0027, always_filler, "Medicine"),
    "Elixir": ItemData(0x0028, always_filler, "Medicine"),
    "Max Elixir": ItemData(0x0029, always_filler, "Medicine"),
    "Lava Cookie": ItemData(0x002A, always_filler, "Medicine"),
    "Berry Juice": ItemData(0x002B, always_filler, "Medicine"),
    "Sacred Ash": ItemData(0x002C, always_useful, "Medicine"),
    "HP Up": ItemData(0x002D, always_filler, "Medicine"),
    "Protein": ItemData(0x002E, always_filler, "Medicine"),
    "Iron": ItemData(0x002F, always_filler, "Medicine"),
    "Carbos": ItemData(0x0030, always_filler, "Medicine"),
    "Calcium": ItemData(0x0031, always_filler, "Medicine"),
    "Rare Candy": ItemData(0x0032, always_useful, "Medicine"),
    "PP Up": ItemData(0x0033, always_filler, "Medicine"),
    "Zinc": ItemData(0x0034, always_filler, "Medicine"),
    "PP Max": ItemData(0x0035, always_filler, "Medicine"),
    "Old Gateau": ItemData(0x0036, always_filler, "Medicine"),
    "Sweet Heart": ItemData(0x0086, always_filler, "Medicine"),
    "Rage Candy Bar": ItemData(0x01F8, always_progression, "Medicine"),
}
