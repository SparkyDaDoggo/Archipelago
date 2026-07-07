from typing import TYPE_CHECKING

from ...locations import PokemonBWLocation

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry


def lookup(domain: int) -> dict[str, int]:
    from ...data.locations.ingame_items.other import table, seasonal

    return {
        name: data.flag_id * 100 + domain + (
            int(name[-2:].split("#")[-1]) if "#" in name[-3:] else 0
        )
        for tab in (table, seasonal)
        for name, data in tab.items()
    }


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ...data.locations.ingame_items.other import table, seasonal
    from ...data.items import all_tm_hm
    from ...data.pokemon import moves

    for tab in (table, seasonal):
        for name, data in tab.items():
            if data.inclusion_rule is None or data.inclusion_rule(world):
                r: "Region" = world.regions[data.region]
                l: PokemonBWLocation = PokemonBWLocation(world.player, name, world.location_name_to_id[name], r)
                l.progress_type = data.progress_type(world)
                if data.rule is not None:
                    l.access_rule = world.rules_dict[data.rule]
                r.locations.append(l)

    chosen = world.random.choice(tuple(a for a in catchable_species_data.items() if a[1].tm_hm_moves.tm_hm_moves))
    world.other_locations_species = chosen[0]
    world.studio_castelia_type = world.random.choice((chosen[1].type_1, chosen[1].type_2))
    chosen_tms = list(chosen[1].tm_hm_moves.tm_hm_moves)
    chosen_tms.sort()
    chosen_tm = world.random.choice(chosen_tms)
    for name in all_tm_hm:
        if name.startswith(chosen_tm):
            world.driftveil_random_tm = name
            world.driftveil_random_move_id = world.move_entries[moves.tm_hm[chosen_tm].move].id
            break
