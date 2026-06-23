from random import Random
from typing import TYPE_CHECKING, Any, Iterable
from collections import ChainMap

from BaseClasses import Item

if TYPE_CHECKING:
    from . import PokemonBWWorld
    from .data import AnyItemData

all_items_view: ChainMap[str, "AnyItemData"] | None = None


class PokemonBWItem(Item):
    game = 'Pokemon Black and White'


def generate_item(name: str, world: "PokemonBWWorld") -> PokemonBWItem:
    global all_items_view

    if all_items_view is None:
        from .data.items import all_items_dict_view
        all_items_view = all_items_dict_view

    data = all_items_view[name]
    # Item id from lookup table is used instead of id from data for safety purposes
    return PokemonBWItem(name, data.classification(world, name), world.item_name_to_id[name], world.player)


def get_item_lookup_table() -> dict[str, int]:
    from .data.items import all_items_dict_view

    return {name: data.item_id for name, data in all_items_dict_view.items()}


def get_main_item_pool(world: "PokemonBWWorld") -> list[PokemonBWItem]:
    from .generate.items import badges, key_items, main_items, seasons, tm_hm

    return (badges.generate_default(world) +
            key_items.generate_default(world) +
            main_items.generate_default(world) +
            seasons.generate_default(world) +
            tm_hm.generate_default(world))


def generate_filler(world: "PokemonBWWorld") -> str:
    if world.filler_nested is None:
        from .data.items import berries, main_items, medicine

        filter_items = (lambda it: True) if not world.options.filler_items_blacklist \
            else (lambda it: it not in world.options.filler_items_blacklist)
        main_filler = tuple(it for it in main_items.filler if filter_items(it))
        main_min_once = tuple(it for it in main_items.min_once if filter_items(it))
        main_mail = tuple(it for it in main_items.mail if filter_items(it))
        berries_standard = tuple(it for it in berries.standard if filter_items(it))
        berries_niche = tuple(it for it in berries.niche if filter_items(it))
        medicine_all = tuple(it for it in medicine.table if filter_items(it))

        main_nested = [
            main_filler,
            main_filler,
            main_filler if not world.options.modify_item_pool.is_useful_filler else [
                main_filler,
                main_min_once,
                main_min_once,
            ],
            main_filler if world.options.modify_item_pool.is_ban_bad_filler else [
                main_filler,
                main_filler,
                main_filler,
                main_mail,
            ],
        ]
        berries_nested = [
            berries_standard,
            berries_standard,
            berries_standard,
            berries_niche,
        ]
        world.filler_nested = [
            main_nested,
            main_nested,
            berries_nested,
            medicine_all,
            medicine_all,
        ]
    return random_choice_nested(world.random, world.filler_nested)


def random_choice_nested(random: Random, nested: Iterable[str | list | tuple | dict]) -> Any:
    """Helper function for getting a random element from a nested list."""
    current: str | Iterable = nested
    while isinstance(current, list | tuple | dict):
        if isinstance(current, list | tuple):
            current = random.choice(current)
        else:
            current = random.choice(tuple(current.keys()))
    return current


def populate_starting_inventory(world: "PokemonBWWorld", items: list[PokemonBWItem]) -> None:
    from .data.items import seasons

    if world.options.season_control == "randomized":
        seasons_list: list["PokemonBWItem"] = [
            item for item in items if item.name in seasons.table
        ]
        start = world.random.choice(seasons_list)
        world.push_precollected(start)
        items.remove(start)


def place_locked_items(world: "PokemonBWWorld", items: list[PokemonBWItem]) -> None:
    from .generate import locked_placement

    locked_placement.place_badges_locked(world, items)
    locked_placement.place_tm_hm_locked(world, items)
