from typing import TYPE_CHECKING

from Options import OptionError
from .. import SpeciesEntry, EvoLine, EvolutionsEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from ...options.stats import PlandoEvolution


def generate_plando_evolutions(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                               by_id: dict[tuple[int, int], SpeciesEntry], plando_evos: list["PlandoEvolution"],
                               base_data: SpeciesEntry) -> list[EvolutionsEntry]:
    from ...data.pokemon.pokedex import by_name as dex_by_name
    from ...data.items import all_items_dict_view

    new_evos: list[EvolutionsEntry] = []
    for plando_evo in plando_evos:
        evo_data = by_id[dex_by_name[plando_evo.species], 0]
        gender_ratio_rando = False  # TODO
        if not gender_ratio_rando:
            if base_data.gender_ratio in (0, 255) and plando_evo.method in ("Level up (female)", "Stone female"):
                raise OptionError(f"{world.player_name}: Plandoing a female-only evolution method "
                                  f"({plando_evo.method}) into a male-only or genderless species "
                                  f"({base_data.species_name}) is not allowed as it leads to impossible evolutions")
            if base_data.gender_ratio in (254, 255) and plando_evo.method in ("Level up (male)", "Stone male"):
                raise OptionError(f"{world.player_name}: Plandoing a male-only evolution method "
                                  f"({plando_evo.method}) into a female-only or genderless species "
                                  f"({base_data.species_name}) is not allowed as it leads to impossible evolutions")
        match plando_evo.method:
            case c if c in ("Level up", "Level up with move",
                            "Level up higher defense", "Level up higher attack", "Level up equal physical",
                            "Level up Silcoon", "Level up Cascoon", "Level up Ninjask", "Level up Shedinja",
                            "Level up (female)", "Level up (male)",
                            "_Level up split", "_Level up PID", "_Level up stats"):
                new_evos.append(EvolutionsEntry(plando_evo.method, plando_evo.level, evo_data))
            case c if c in ("Stone", "Stone male", "Stone female"):
                new_evos.append(EvolutionsEntry(plando_evo.method, all_items_dict_view[plando_evo.stone].item_id, evo_data))
            case c if c in ("Trade with item", "Level up item day", "Level up item night", "_Level up item"):
                new_evos.append(EvolutionsEntry(plando_evo.method, all_items_dict_view[plando_evo.held].item_id, evo_data))
            case "Level up with move":
                new_evos.append(EvolutionsEntry(plando_evo.method, world.move_entries[plando_evo.move].id, evo_data))
            case "Level up with party member":
                partner_num = all_species[plando_evo.partner].dex_number \
                    if plando_evo.partner in all_species else dex_by_name[plando_evo.partner]
                new_evos.append(EvolutionsEntry(plando_evo.method, partner_num, evo_data))
            case "_Level up item":
                item_id = all_items_dict_view[plando_evo.held].item_id
                new_evos.append(EvolutionsEntry("Level up item day", item_id, evo_data))
                new_evos.append(EvolutionsEntry("Level up item night", item_id, evo_data))
            case "_Level up split":
                evo_2_data = by_id[dex_by_name[plando_evo.species_2], 0]
                new_evos.append(EvolutionsEntry("Level up Ninjask", plando_evo.level, evo_data))
                new_evos.append(EvolutionsEntry("Level up Shedinja", plando_evo.level, evo_2_data))
            case "_Level up PID":
                evo_2_data = by_id[dex_by_name[plando_evo.species_2], 0]
                new_evos.append(EvolutionsEntry("Level up Silcoon", plando_evo.level, evo_data))
                new_evos.append(EvolutionsEntry("Level up Cascoon", plando_evo.level, evo_2_data))
            case "_Level up stats":
                evo_2_data = by_id[dex_by_name[plando_evo.species_2], 0]
                evo_3_data = by_id[dex_by_name[plando_evo.species_3], 0]
                new_evos.append(EvolutionsEntry("Level up higher defense", plando_evo.level, evo_data))
                new_evos.append(EvolutionsEntry("Level up higher attack", plando_evo.level, evo_2_data))
                new_evos.append(EvolutionsEntry("Level up equal physical", plando_evo.level, evo_3_data))
            case _:
                new_evos.append(EvolutionsEntry(plando_evo.method, 0, evo_data))
    return new_evos


def plando_evolutions(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                      by_id: dict[tuple[int, int], SpeciesEntry]):

    # Is always run, even without plando
    if world.options.randomize_evolutions.is_randomize:
        for data in all_species.values():
            if data.form:
                continue
            data.evolutions.clear()
            data.pre_evolutions.clear()
            data.write |= 0b1

    def update_evo_stuff(_data: SpeciesEntry, _target_data: SpeciesEntry):
        if _data == _target_data:
            return
        if world.options.randomize_evolutions.is_randomize:
            if _data.evo_line and _target_data.evo_line:
                if _data.evo_line.search() != _target_data.evo_line.search():
                    _data.evo_line.merge(_target_data.evo_line)
            elif _data.evo_line:
                _data.evo_line.search().members.add(_target_data.dex_number)
                _target_data.evo_line = _data.evo_line
            elif _target_data.evo_line:
                _target_data.evo_line.search().members.add(_data.dex_number)
                _data.evo_line = _target_data.evo_line
            else:
                evo_line = EvoLine()
                evo_line.type = _data.types[0] if _data.types[0] in _target_data.types else _data.types[1]
                evo_line.members = {_data.dex_number, _target_data.dex_number}
                _data.evo_line = _target_data.evo_line = evo_line
        _target_data.pre_evolutions[_data] = True

    for spec_name, plando_stat in world.options.stats_plando:
        if plando_stat.evolutions is False:
            continue
        data = all_species[spec_name]
        if data.form:  # Custom forms actually can't have their own evolutions
            continue
        new_evos = generate_plando_evolutions(world, all_species, by_id, plando_stat.evolutions, data)
        for evo_entry in new_evos:
            update_evo_stuff(data, evo_entry.species)
        data.evolutions += new_evos
        data.write |= 0b1
        if plando_stat.override_evolutions:
            data.write |= 0b10
