from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def set_value(data: SpeciesEntry, stats: tuple[int, ...]):
    data.base_stats = stats
    if not data.is_custom_form:
        for form_data in data.all_forms:
            if not form_data.is_custom_form:
                form_data.base_stats = data.base_stats


def randomize_stats_pre_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):

    mods = world.options.randomize_base_stats

    if not mods.is_randomize:
        for plando_name, plando_stat in world.options.stats_plando:
            data = all_species[plando_name]
            set_value(data, (plando_stat.base_hp or data.base_stats[0],
                             plando_stat.base_attack or data.base_stats[1],
                             plando_stat.base_defense or data.base_stats[2],
                             plando_stat.base_sp_attack or data.base_stats[3],
                             plando_stat.base_sp_defense or data.base_stats[4],
                             plando_stat.base_speed or data.base_stats[5]))
        return

    for data in all_species.values():
        data.base_stats = (0, 0, 0, 0, 0, 0)
        data.write |= 0b100

    if mods.is_follow_evolutions:  # Do later in case of evo rando, evo rando can work with nullified base stats
        return

    max_total = world.options.stats_randomization_adjustments["Stats total maximum"]
    min_total = world.options.stats_randomization_adjustments["Stats total minimum"]

    for data in all_species.values():
        if data.base_stats[0]:
            continue
        if data.form and not data.is_custom_form:
            continue
        total = sum(data.base_stats_copy) if not mods.is_random_total else world.random.randint(min_total, max_total)
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
        set_value(data, tuple(dist))
        if data.species_name in world.options.stats_plando:
            plando_stat = world.options.stats_plando[data.species_name]
            set_value(data, (plando_stat.base_hp or data.base_stats[0],
                             plando_stat.base_attack or data.base_stats[1],
                             plando_stat.base_defense or data.base_stats[2],
                             plando_stat.base_sp_attack or data.base_stats[3],
                             plando_stat.base_sp_defense or data.base_stats[4],
                             plando_stat.base_speed or data.base_stats[5]))


def randomize_stats_post_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):

    mods = world.options.randomize_base_stats

    if not mods.is_randomize or not mods.is_follow_evolutions:
        return

    max_total = world.options.stats_randomization_adjustments["Stats total maximum"]
    min_total = world.options.stats_randomization_adjustments["Stats total minimum"]

    def roll(data: SpeciesEntry, pre: list[int] | tuple[int, ...]):
        total = max(sum(pre) + 1, sum(data.base_stats_copy)) if not mods.is_random_total \
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
        set_value(data, tuple(dist))
        apply_plando(data)
        do_evos(data, dist)

    def apply_plando(data: SpeciesEntry):
        if data.species_name in world.options.stats_plando:
            plando_stat = world.options.stats_plando[data.species_name]
            set_value(data, (plando_stat.base_hp or data.base_stats[0],
                             plando_stat.base_attack or data.base_stats[1],
                             plando_stat.base_defense or data.base_stats[2],
                             plando_stat.base_sp_attack or data.base_stats[3],
                             plando_stat.base_sp_defense or data.base_stats[4],
                             plando_stat.base_speed or data.base_stats[5]))

    def upgrade(data: SpeciesEntry, pre: list[int] | tuple[int, ...]):
        old = data.base_stats
        set_value(data, tuple(max(data.base_stats[i], pre[i]) for i in range(6)))
        apply_plando(data)
        if data.base_stats != old:
            do_evos(data, data.base_stats)

    def do_evos(data: SpeciesEntry, this: tuple[int, ...] | list[int]):
        for evo_tup in data.evolutions:
            evo_spec = evo_tup.species.by_form(data.form)
            if not evo_spec.base_stats[0]:
                roll(evo_spec, this)
            else:
                upgrade(evo_spec, this)

    for dat in all_species.values():
        if not dat.base_stats[0] and (not dat.form or dat.is_custom_form):
            roll(dat, (0, 0, 0, 0, 0, 0))
