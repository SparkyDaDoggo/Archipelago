from typing import TextIO, TYPE_CHECKING

if TYPE_CHECKING:
    from .. import PokemonBWWorld


def write_spoiler_encounter(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:
    from ..data.locations.encounters.region_connections import connections, connection_by_region
    from ..data.pokemon.species import by_id
    from ..data.pokemon.pokedex import by_number

    if world.options.randomize_wild_pokemon.is_randomize or world.options.encounter_plando:

        methods: dict[str, list[str]] = {name: [] for name in connections}
        for name, data in world.wild_encounter.items():
            region = name[:name.rfind(" ")]
            methods[connection_by_region[region]].append(by_id[data.species_id])

        spoiler_handle.write(f"\n\nPokemon locations ({world.player_name}):\n\n")
        for method, species in methods.items():
            spoiler_handle.write(method+": "+(", ".join(species))+"\n")

        for name, data in world.static_encounter.items():
            spoiler_handle.write(name+": "+by_id[data.species_id]+"\n")
        for name, data in world.trade_encounter.items():
            spoiler_handle.write(name+": "+by_id[data.species_id]+" for "+by_number[data.wanted_dex_number]+"\n")


def write_spoiler_trainer(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:

    if world.options.randomize_trainer_pokemon.is_randomize:

        teams: dict[int, list[str]] = {}
        for entry in world.trainer_teams:
            if entry.team_number not in teams:
                teams[entry.team_number] = []
            teams[entry.team_number].append(entry.species)

        spoiler_handle.write(f"\n\nTrainer teams ({world.player_name}, Trainer names are WIP):\n\n")
        for trainer, species in teams.items():
            spoiler_handle.write(f"Trainer #{trainer}: "+(", ".join(species))+"\n")


def write_spoiler_evolutions(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:
    from ..data.pokemon.pokedex import by_number

    if world.options.randomize_evolutions.is_randomize or world.options.stats_plando:

        spoiler_handle.write(f"\n\nEvolutions ({world.player_name}, each entry in the format "
                             f"<method, value, species>):\n\n")
        for name, data in world.species_entries.items():
            spoiler_handle.write(f"{name}: "+(" | ".join(f"{evo[0]}, {evo[1]}, {by_number[evo[2]]}"
                                                         for evo in data.evolutions))+"\n")


def write_spoiler_stats(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:

    if (
        world.options.randomize_base_stats.is_randomize
        or world.options.randomize_catch_rates
        or world.options.stats_plando
    ):

        spoiler_handle.write(f"\n\nStats ({world.player_name}, the format is <hp, attack, defense, special attack, "
                             f"special defense, speed, catch rate>):\n\n")
        for name, data in world.species_entries.items():
            spoiler_handle.write(f"{name}: {data.base_hp}, {data.base_attack}, {data.base_defense}, "
                                 f"{data.base_sp_attack}, {data.base_sp_defense}, {data.base_speed}, "
                                 f"{data.catch_rate}, \n")


def write_spoiler_levelup_movesets(world: "PokemonBWWorld", spoiler_handle: TextIO) -> None:

    if world.options.randomize_level_up_movesets.is_randomize or world.options.stats_plando:

        spoiler_handle.write(f"\n\nLevelup movesets ({world.player_name}, with each entry having the format <level, "
                             f"move name>):\n\n")
        for name, data in world.species_entries.items():
            spoiler_handle.write(f"{name}: "+str(data.level_up_moves.level_up_moves).replace("'", "")+"\n")
