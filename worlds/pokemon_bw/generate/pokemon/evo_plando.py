from typing import TYPE_CHECKING

from Options import OptionError
from .. import SpeciesEntry, EvoLine

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from ...options.stats import PlandoEvolution


def generate_plando_evolutions(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                               by_id: dict[tuple[int, int], SpeciesEntry], plando_evos: list["PlandoEvolution"],
                               base_data: SpeciesEntry) -> list[tuple[str, int, tuple[SpeciesEntry, ...]]]:
    from ...data.pokemon.pokedex import by_name as dex_by_name
    from ...data.items import all_items_dict_view

    def all_datas_by_dex(_dex_name: str) -> tuple[SpeciesEntry, ...]:
        _evo_dex = dex_by_name[_dex_name]
        _evo_datas = ()
        for _form in range(6):
            if (_evo_dex, _form) not in by_id:
                break
            _evo_data = by_id[_evo_dex, _form]
            if _form and not _evo_data.is_custom_form:
                break
            _evo_datas += (_evo_data, )
        return _evo_datas

    new_evos: list[tuple[str, int, tuple[SpeciesEntry, ...]]] = []
    for plando_evo in plando_evos:
        evo_datas = all_datas_by_dex(plando_evo.species)
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
                new_evos.append((plando_evo.method, plando_evo.level, evo_datas))
            case c if c in ("Stone", "Stone male", "Stone female"):
                new_evos.append((plando_evo.method, all_items_dict_view[plando_evo.stone].item_id, evo_datas))
            case c if c in ("Trade with item", "Level up item day", "Level up item night", "_Level up item"):
                new_evos.append((plando_evo.method, all_items_dict_view[plando_evo.held].item_id, evo_datas))
            case "Level up with move":
                new_evos.append((plando_evo.method, world.move_entries[plando_evo.move].id, evo_datas))
            case "Level up with party member":
                partner_num = all_species[plando_evo.partner].dex_number \
                    if plando_evo.partner in all_species else dex_by_name[plando_evo.partner]
                new_evos.append((plando_evo.method, partner_num, evo_datas))
            case "_Level up item":
                item_id = all_items_dict_view[plando_evo.held].item_id
                new_evos.append(("Level up item day", item_id, evo_datas))
                new_evos.append(("Level up item night", item_id, evo_datas))
            case "_Level up split":
                evo_2_datas = all_datas_by_dex(plando_evo.species_2)
                new_evos.append(("Level up Ninjask", plando_evo.level, evo_datas))
                new_evos.append(("Level up Shedinja", plando_evo.level, evo_2_datas))
            case "_Level up PID":
                evo_2_datas = all_datas_by_dex(plando_evo.species_2)
                new_evos.append(("Level up Silcoon", plando_evo.level, evo_datas))
                new_evos.append(("Level up Cascoon", plando_evo.level, evo_2_datas))
            case "_Level up stats":
                evo_2_datas = all_datas_by_dex(plando_evo.species_2)
                evo_3_datas = all_datas_by_dex(plando_evo.species_3)
                new_evos.append(("Level up higher defense", plando_evo.level, evo_datas))
                new_evos.append(("Level up higher attack", plando_evo.level, evo_2_datas))
                new_evos.append(("Level up equal physical", plando_evo.level, evo_3_datas))
            case _:
                new_evos.append((plando_evo.method, 0, evo_datas))
    return new_evos


def plando_evolutions_override(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                               by_id: dict[tuple[int, int], SpeciesEntry]):

    if world.options.randomize_evolutions.is_randomize:  # Always run, even without plando
        for data in all_species.values():
            data.evolutions.clear()
            data.pre_evolutions.clear()
            data.write |= 1

    def update_evo_stuff(_data: SpeciesEntry, _target_data: SpeciesEntry):
        if _data == _target_data:
            return
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
        if not plando_stat.override_evolutions or plando_stat.evolutions is False:
            continue
        data = all_species[spec_name]
        new_evos = generate_plando_evolutions(world, all_species, by_id, plando_stat.evolutions, data)
        for evo_tup in new_evos:
            for evo_entry in evo_tup[2]:
                update_evo_stuff(data, evo_entry)
        data.evolutions = new_evos
        data.write |= 3


def plando_evolutions_append(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                             by_id: dict[tuple[int, int], SpeciesEntry]):

    def update_evo_stuff(_data: SpeciesEntry, _target_data: SpeciesEntry):
        if _data == _target_data:
            return
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

    for poke, plando_stat in world.options.stats_plando:
        if plando_stat.override_evolutions or plando_stat.evolutions is False:
            continue
        data = all_species[poke]
        new_evos = generate_plando_evolutions(world, all_species, by_id, plando_stat.evolutions, data)
        if len(data.evolutions) + len(new_evos) > 7:
            raise OptionError(f"{world.player_name}: Evolution plando tries to add {len(new_evos)} new evolutions to "
                              f"{poke}, which already has {len(data.evolutions)} evolutions, thereby exceeding the "
                              f"limit of 7 evolutions per species")
        for evo_tup in new_evos:
            for evo_entry in evo_tup[2]:
                update_evo_stuff(data, evo_entry)
        data.evolutions += new_evos
        data.write |= 1
