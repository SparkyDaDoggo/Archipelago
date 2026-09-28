from typing import TYPE_CHECKING, ChainMap

from ...data import ItemData
from ...items import PokemonBWItem

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_default(world: "PokemonBWWorld") -> list[PokemonBWItem]:
    from ...data.items.key_items import progression, vanilla, useless, special
    from ...data.items.medicine import important as med_important
    from ...data.items.main_items import fossils

    items = [
        PokemonBWItem(name, data.classification(world, name), data.item_id, world.player)
        for name, data in ChainMap[str, ItemData](progression, vanilla, med_important, fossils).items()
    ]

    if world.options.modify_item_pool.is_useless_key_items:
        items += [
            PokemonBWItem(name, data.classification(world, name), data.item_id, world.player)
            for name, data in useless.items() if name not in world.options.filler_items_blacklist
        ]

    data = special["Xtransceiver (Blue)"]
    items.append(PokemonBWItem("Xtransceiver (Blue)", data.classification(world, "Xtransceiver (Blue)"), data.item_id, world.player))
    if world.options.version == "black":
        data = special["Light Stone"]
        items.append(PokemonBWItem("Light Stone", data.classification(world, "Light Stone"), data.item_id, world.player))
    elif world.options.version == "white":
        data = special["Dark Stone"]
        items.append(PokemonBWItem("Dark Stone", data.classification(world, "Dark Stone"), data.item_id, world.player))
    else:
        stone = world.random.choice(("Light Stone", "Dark Stone"))
        data = special[stone]
        items.append(PokemonBWItem(stone, data.classification(world, stone), data.item_id, world.player))

    return items
