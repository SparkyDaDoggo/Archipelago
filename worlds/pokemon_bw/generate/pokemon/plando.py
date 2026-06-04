from typing import TYPE_CHECKING, Callable

from Options import OptionError
from .. import SpeciesEntry, EvoLine
from ...data import SpeciesData

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from ...options import PlandoEvolution


def generate_plando_evolutions(plando_evos: list["PlandoEvolution"], all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.pokedex import by_name as dex_by_name
    from ...data.items import all_items_dict_view
    from ...data.pokemon.moves import by_name as move_by_name

    new_evos = []
    for plando_evo in plando_evos:
        spec_num = all_species[plando_evo.species].dex_number \
            if plando_evo.species in all_species else dex_by_name[plando_evo.species]
        match plando_evo.method:
            case c if c in ("Level up", "Level up with move",
                            "Level up higher defense", "Level up higher attack", "Level up equal physical",
                            "Level up Silcoon", "Level up Cascoon", "Level up Ninjask", "Level up Shedinja",
                            "Level up (female)", "Level up (male)",
                            "_Level up split", "_Level up PID", "_Level up stats"):
                new_evos.append((plando_evo.method, plando_evo.level, spec_num))
            case c if c in ("Stone", "Stone male", "Stone female"):
                new_evos.append((plando_evo.method, all_items_dict_view[plando_evo.stone].item_id, spec_num))
            case c if c in ("Trade with item", "Level up item day", "Level up item night", "_Level up item"):
                new_evos.append((plando_evo.method, all_items_dict_view[plando_evo.held].item_id, spec_num))
            case "Level up with move":
                new_evos.append((plando_evo.method, move_by_name[plando_evo.move], spec_num))
            case "Level up with party member":
                partner_num = all_species[plando_evo.partner].dex_number \
                    if plando_evo.partner in all_species else dex_by_name[plando_evo.partner]
                new_evos.append((plando_evo.method, partner_num, spec_num))
            case "_Level up item":
                item_id = all_items_dict_view[plando_evo.held].item_id
                new_evos.append(("Level up item day", item_id, spec_num))
                new_evos.append(("Level up item night", item_id, spec_num))
            case "_Level up split":
                new_evos.append(("Level up Ninjask", plando_evo.level, spec_num))
                new_evos.append(("Level up Shedinja", plando_evo.level, spec_num))
            case "_Level up PID":
                new_evos.append(("Level up Silcoon", plando_evo.level, spec_num))
                new_evos.append(("Level up Cascoon", plando_evo.level, spec_num))
            case "_Level up stats":
                new_evos.append(("Level up higher defense", plando_evo.level, spec_num))
                new_evos.append(("Level up higher attack", plando_evo.level, spec_num))
                new_evos.append(("Level up equal physical", plando_evo.level, spec_num))
            case _:
                new_evos.append((plando_evo.method, 0, spec_num))
    return new_evos


def plando_evolutions_override(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.species import by_id
    from ...data.pokemon.pokedex import by_name as dex_by_name

    def update_evo_stage(_data: SpeciesEntry, stage: int):
        if _data.evolution_stage < stage:
            _data.evolution_stage = stage
            if stage < 3:
                for _evo in _data.evolutions:
                    update_evo_stage(all_species[by_id[(_evo[2], 0)]], stage + 1)

    def update_evo_stuff(_data: SpeciesEntry, _target_data: SpeciesEntry):
        if _data.evo_line and _target_data.evo_line:
            if _data.evo_line.search() != _target_data.evo_line.search():
                _data.evo_line.merge(_target_data.evo_line)
            update_evo_stage(_target_data, _data.evolution_stage + 1)
        elif _data.evo_line:
            _data.evo_line.search().members.add(_target_data.dex_number)
            _target_data.evo_line = _data.evo_line
        elif _target_data.evo_line:
            _target_data.evo_line.search().members.add(_data.dex_number)
            _data.evo_line = _target_data.evo_line
            _data.evolution_stage = 1
            update_evo_stage(_target_data, 2)
        else:
            evo_line = EvoLine()
            evo_line.type = _data.type_1 if _data.type_1 in (_target_data.type_1, _target_data.type_2) else _data.type_2
            evo_line.members = {_data.dex_number, _target_data.dex_number}
            _data.evo_line = _target_data.evo_line = evo_line
            _data.evolution_stage, _target_data.evolution_stage = 1, 2

    for poke, plando_stat in world.options.stats_plando:
        if not plando_stat.override_evolutions or plando_stat.evolutions is False:
            continue
        spec_name = poke if poke in all_species else by_id[(dex_by_name[poke], 0)]
        data = all_species[spec_name]
        new_evos = generate_plando_evolutions(plando_stat.evolutions, all_species)
        for evo_tup in new_evos:
            for form in range(6):
                evo_data = all_species[by_id[(evo_tup[2], form)]]
                if form and not evo_data.is_custom_form:
                    break
                if world.options.randomize_evolutions.is_randomize:
                    data.evolution_stage = 1
                update_evo_stuff(data, evo_data)
        data.evolutions = new_evos
        data.write |= 3


def plando_evolutions_append(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.species import by_id
    from ...data.pokemon.pokedex import by_name as dex_by_name

    def update_evo_stage(_data: SpeciesEntry, stage: int):
        if _data.evolution_stage < stage:
            _data.evolution_stage = stage
            if stage < 3:
                for _evo in _data.evolutions:
                    update_evo_stage(all_species[by_id[(_evo[2], 0)]], stage + 1)

    for poke, plando_stat in world.options.stats_plando:
        if plando_stat.override_evolutions or plando_stat.evolutions is False:
            continue
        data = all_species[poke if poke in all_species else by_id[(dex_by_name[poke], 0)]]
        new_evos = generate_plando_evolutions(plando_stat.evolutions, all_species)
        if len(data.evolutions) + len(new_evos) > 7:
            raise OptionError(f"{world.player_name}: Evolution plando tries to add {len(new_evos)} new evolutions to "
                              f"{poke}, which already has {len(data.evolutions)} evolutions, thereby exceeding the "
                              f"limit of 7 evolutions per species")
        for evo_tup in new_evos:
            for form in range(6):
                evo_data = all_species[by_id[(evo_tup[2], form)]]
                if form and not evo_data.is_custom_form:
                    break
                update_evo_stage(evo_data, data.evolution_stage+1)
        data.evolutions += new_evos
        data.write |= 1
