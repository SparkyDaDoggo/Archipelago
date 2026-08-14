from typing import TextIO, TYPE_CHECKING

from ..options.moves import PlandoTypeEffect, PlandoMoveData

if TYPE_CHECKING:
    from .. import PokemonBWWorld


def write_spoiler_encounter(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:
    from ..data.locations.encounters.region_connections import connections
    from ..data.pokemon.species import by_id
    from ..data.pokemon.pokedex import by_number

    if world.options.randomize_wild_pokemon.is_randomize or world.options.encounter_plando:

        methods: dict[tuple[str, str, str], list[str]] = {con.entering_region: [] for con in connections}
        for data in world.wild_encounter.values():
            methods[data.encounter_region].append(by_id[data.species_id].species_name)

        spoiler_handle.write(f"\n\nPokemon locations ({world.player_name}):\n\n")
        for method, species in methods.items():
            m_name = f"{method[0]}"
            if method[1]:
                m_name += f" ({method[1]})"
            m_name += " - " + method[2]
            spoiler_handle.write(m_name+": "+(", ".join(species))+"\n")

        for name, data in world.static_encounter.items():
            spoiler_handle.write(name+": "+by_id[data.species_id].species_name+"\n")
        for name, data in world.trade_encounter.items():
            spoiler_handle.write(name+": "+by_id[data.species_id].species_name+" for "+by_number[data.wanted_dex_number]+"\n")


def write_spoiler_trainer(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:

    if world.options.randomize_trainer_pokemon.is_randomize:

        teams: dict[int, list[str]] = {}
        for entry in world.trainer_teams:
            if entry.team_number not in teams:
                teams[entry.trainer_id] = []
            teams[entry.trainer_id].append(f"{entry.species} Lv.{entry.level}")

        spoiler_handle.write(f"\n\nTrainer teams ({world.player_name}, Trainer names are WIP):\n\n")
        for trainer, species in teams.items():
            spoiler_handle.write(f"Trainer #{trainer}: "+(", ".join(species))+"\n")


def write_spoiler_evolutions(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:

    if world.options.randomize_evolutions.is_randomize or any(data.evolutions is not False
                                                              for data in world.options.stats_plando.value.values()):

        spoiler_handle.write(f"\n\nEvolutions ({world.player_name}, each entry in the format "
                             f"<method, value, species>):\n\n")
        for name, data in world.species_entries.items():
            spoiler_handle.write(f"{name}: "+(" | ".join(f"{evo[0]}, {evo[1]}, {evo[2][0].dex_name}"
                                                         for evo in data.evolutions))+"\n")


def write_spoiler_stats(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:

    if (
        world.options.randomize_base_stats.is_randomize
        or world.options.randomize_catch_rates.is_randomize
        or world.options.randomize_types.is_randomize
        or any((data.base_hp or data.base_attack or data.base_defense or data.base_sp_attack or data.base_sp_defense
                or data.base_speed or data.catch_rate or data.types)
               for data in world.options.stats_plando.value.values())
    ):

        spoiler_handle.write(f"\n\nStats ({world.player_name}, the format is <type(s), hp, attack, defense, "
                             f"special attack, special defense, speed, catch rate, egg group(s), egg species> "
                             f"(last two only if randomized/plando'd)):\n\n")
        for name, data in world.species_entries.items():
            line = [data.types[0]]
            if data.types[0] != data.types[1]:
                line.append(data.types[1])
            line.extend(str(s) for s in data.base_stats)
            line.append(str(data.catch_rate))
            if data.egg_groups is not None:
                line.append(data.egg_groups[0])
                if data.egg_groups[0] != data.egg_groups[1]:
                    line.append(data.egg_groups[1])
            if data.egg_species is not None:
                line.append(data.egg_species)
            spoiler_handle.write(f"{name}: {', '.join(line)}\n")


def write_spoiler_levelup_movesets(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:

    if world.options.randomize_level_up_movesets.is_randomize or any(data.levelup_moveset is not False for data in
                                                                     world.options.stats_plando.value.values()):

        spoiler_handle.write(f"\n\nLevelup movesets ({world.player_name}, with each entry having the format <level, "
                             f"move name>):\n\n")
        for name, data in world.species_entries.items():
            spoiler_handle.write(f"{name}: "+str(data.level_up_moves.level_up_moves).replace("'", "")+"\n")


def write_spoiler_tm_hm_compat(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:

    if world.options.randomize_tm_hm_compatibility.is_randomize or any(data.tm_hm_compatibility for data in
                                                                       world.options.stats_plando.value.values()):

        spoiler_handle.write(f"\n\nTM/HM compatibility ({world.player_name}):\n\n")
        for name, data in world.species_entries.items():
            spoiler_handle.write(f"{name}: {', '.join(data.tm_hm_moves.tm_hm_moves)}\n")


def write_spoiler_move_data(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:
    pass  # TODO


def write_spoiler_type_chart(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:
    pass  # TODO
