from typing import TYPE_CHECKING, Callable
from .. import SpeciesEntry
from ...data import SpeciesData

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def plando_stats(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]) -> list[str]:
    from ...data.pokemon.pokedex import by_name as dex_by_name
    from ...data.pokemon.species import by_id

    all_plandod = []

    for species, plando_stat in world.options.stats_plando:
        if any((plando_stat.base_hp, plando_stat.base_attack, plando_stat.base_defense,
                plando_stat.base_sp_attack, plando_stat.base_sp_defense, plando_stat.base_speed)):
            actual_spec = by_id[(dex_by_name[species], 0)] if species not in all_species else species
            data = all_species[actual_spec]
            data.write |= 0b100
            data.base_hp = plando_stat.base_hp or data.base_hp
            data.base_attack = plando_stat.base_attack or data.base_attack
            data.base_defense = plando_stat.base_defense or data.base_defense
            data.base_sp_attack = plando_stat.base_sp_attack or data.base_sp_attack
            data.base_sp_defense = plando_stat.base_sp_defense or data.base_sp_defense
            data.base_speed = plando_stat.base_speed or data.base_speed
            all_plandod.append(actual_spec)

    return all_plandod


def randomize_stats_pre_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.species import by_name, by_id

    mods = world.options.randomize_base_stats

    if not mods.is_randomize:
        plando_stats(world, all_species)
        return

    for species, data in all_species.items():
        data.base_hp, data.base_attack, data.base_defense, data.base_sp_attack, data.base_sp_defense, data.base_speed \
            = 0, 0, 0, 0, 0, 0
        data.write |= 0b100

    if mods.is_follow_evolutions:
        return

    plando_stats(world, all_species)

    max_total = world.options.stats_randomization_adjustments["Stats total maximum"]
    min_total = world.options.stats_randomization_adjustments["Stats total minimum"]
    stats_total: Callable[[SpeciesEntry | SpeciesData], int] = lambda _d: (
        _d.base_hp + _d.base_attack + _d.base_defense +
        _d.base_sp_attack + _d.base_sp_defense + _d.base_speed
    )

    for species, data in all_species.items():
        if data.base_hp:
            continue
        if data.form and not data.is_custom_form:
            continue
        total = stats_total(by_name[species]) if not mods.is_random_total else world.random.randint(min_total, max_total)
        individual = tuple(world.random.randint(1, 255) for _ in range(6))
        dist = [int(n / sum(individual) * total) for n in individual]
        cache = total - sum(dist)
        for i in range(6):
            if dist[i] > 255:
                cache += dist[i] - 255
                dist[i] = 255
            if dist[i] == 0:
                cache -= 1
                dist[i] = 1
        if cache:
            for i in range(6):
                if cache > 0 and dist[i] < 255:
                    to_add = min(cache, 255 - dist[i])
                    cache -= to_add
                    dist[i] += to_add
                if cache < 0 and dist[i] > 1:
                    to_sub = min(cache, dist[i] - 1)
                    cache += to_sub
                    dist[i] -= to_sub
                if cache == 0:
                    break
            else:
                raise Exception(f"Error with distributing cache in base stats rando: "
                                f"cache = {cache}, dist = {dist}, total = {total}, max_total = {max_total}, "
                                f"min_total = {min_total}, individual = {individual}")
        data.base_hp, data.base_attack, data.base_defense, data.base_sp_attack, data.base_sp_defense, data.base_speed \
            = dist
    for species, data in all_species.items():
        if data.form and not data.is_custom_form:
            base_data = all_species[by_id[(data.dex_number, 0)]]
            data.base_hp, data.base_attack, data.base_defense, data.base_sp_attack, data.base_sp_defense, data.base_speed \
                = base_data.base_hp, base_data.base_attack, base_data.base_defense, base_data.base_sp_attack, base_data.base_sp_defense, base_data.base_speed


def randomize_stats_post_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.species import by_name, by_id

    mods = world.options.randomize_base_stats

    if not mods.is_randomize or not mods.is_follow_evolutions:
        return

    plandod_species = plando_stats(world, all_species)

    max_total = world.options.stats_randomization_adjustments["Stats total maximum"]
    min_total = world.options.stats_randomization_adjustments["Stats total minimum"]
    stats_total: Callable[[SpeciesEntry | SpeciesData], int] = lambda _d: (
        _d.base_hp + _d.base_attack + _d.base_defense +
        _d.base_sp_attack + _d.base_sp_defense + _d.base_speed
    )

    def roll(species: str, data: SpeciesEntry, pre: list[int] | tuple[int, ...]):
        total = max(sum(pre) + 1, stats_total(by_name[species])) if not mods.is_random_total \
            else world.random.randint(max(min(sum(pre) + 1, max_total), min_total), max_total)
        append = tuple(world.random.randint(1, 255) for _ in range(6))
        dist = [pre[i] + int(append[i] / sum(append) * (total - sum(pre))) for i in range(6)]
        cache = total - sum(dist)
        for i in range(6):
            if dist[i] > 255:
                cache += dist[i] - 255
                dist[i] = 255
            if dist[i] == 0:
                cache -= 1
                dist[i] = 1
        if cache:
            for i in range(6):
                if cache > 0 and dist[i] < 255:
                    to_add = min(cache, 255 - dist[i])
                    cache -= to_add
                    dist[i] += to_add
                if cache < 0 and dist[i] > pre[i]:
                    to_sub = min(cache, dist[i] - pre[i])
                    cache += to_sub
                    dist[i] -= to_sub
                if cache == 0:
                    break
            else:
                raise Exception(f"Error with distributing cache in base stats rando: "
                                f"cache = {cache}, dist = {dist}, total = {total}, max_total = {max_total}, "
                                f"min_total = {min_total}, append = {append}")
        data.base_hp, data.base_attack, data.base_defense, data.base_sp_attack, data.base_sp_defense, data.base_speed \
            = dist
        do_evos(data, dist)

    def upgrade(data: SpeciesEntry, pre: list[int] | tuple[int, ...]):
        this = (data.base_hp, data.base_attack, data.base_defense, data.base_sp_attack, data.base_sp_defense, data.base_speed)
        if all(this[i] == pre[i] for i in range(6)):
            return
        data.base_hp = max(data.base_hp, pre[0])
        data.base_attack = max(data.base_attack, pre[0])
        data.base_defense = max(data.base_defense, pre[0])
        data.base_sp_attack = max(data.base_sp_attack, pre[0])
        data.base_sp_defense = max(data.base_sp_defense, pre[0])
        data.base_speed = max(data.base_speed, pre[0])
        data.base_speed = min(data.base_speed + 1, 255)
        this = (data.base_hp, data.base_attack, data.base_defense, data.base_sp_attack, data.base_sp_defense, data.base_speed)
        do_evos(data, this)

    def do_evos(data: SpeciesEntry, this: tuple[int, ...] | list[int]):
        for evo_tup in data.evolutions:
            for form in range(6):
                if (data.dex_number, form) not in by_id:
                    break
                evo_id_tup = (evo_tup[2], form)
                evo_species = by_id[evo_id_tup if evo_id_tup in by_id else (evo_tup[2], 0)]
                evo_dat = all_species[evo_species]
                if form and not evo_dat.is_custom_form:
                    break
                if not evo_dat.base_hp:
                    roll(evo_species, evo_dat, this)
                elif evo_species not in plandod_species and (evo_dat.evo_line is None or data.dex_number not in evo_dat.evo_line):
                    upgrade(evo_dat, this)

    for spec in plandod_species:
        dat = all_species[spec]
        do_evos(dat, (dat.base_hp, dat.base_attack, dat.base_defense, dat.base_sp_attack, dat.base_sp_defense, dat.base_speed))
    for spec, dat in all_species.items():
        if not dat.base_hp and (not dat.form or dat.is_custom_form):
            roll(spec, dat, (0, 0, 0, 0, 0, 0))
    for spec, dat in all_species.items():
        if dat.form and not dat.is_custom_form:
            base_data = all_species[by_id[(dat.dex_number, 0)]]
            dat.base_hp, dat.base_attack, dat.base_defense, dat.base_sp_attack, dat.base_sp_defense, dat.base_speed \
                = base_data.base_hp, base_data.base_attack, base_data.base_defense, base_data.base_sp_attack, base_data.base_sp_defense, base_data.base_speed
