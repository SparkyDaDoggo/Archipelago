import itertools
from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def plando_types(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]) -> list[str]:

    all_plandod = []

    for species, plando_stat in world.options.stats_plando:
        if plando_stat.types:
            data = all_species[species]
            data.write |= 0b100000
            data.types = plando_stat.types * (3 - len(plando_stat.types))
            all_plandod.append(species)

    return all_plandod


def randomize_types_pre_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                            by_id: dict[tuple[int, int], SpeciesEntry]):
    from ...data.pokemon.species import by_name
    from ...data.pokemon.types import by_name as types_by_name

    mods = world.options.randomize_types

    if not mods.is_randomize:
        plando_types(world, all_species)
        return

    for dat in all_species.values():
        dat.types = ("", "")
        dat.write |= 0b100000

    if mods.is_force_evolutions or not (world.options.randomize_evolutions.is_common_type
                                        or world.options.randomize_evolutions.is_follow_type):
        return

    plandod_ts = plando_types(world, all_species)
    dual_single = (mods.is_dual_only * 2 + mods.is_single_only) % 3
    combinations = {(t1, t2): 0 for t1 in types_by_name for t2 in types_by_name}
    for spec, dat in by_name.items():
        combinations[dat.types] += 1
        if dat.types[0] != dat.types[1]:
            combinations[dat.types[1], dat.types[0]] += 1
    if dual_single == 2:
        for t in types_by_name:
            combinations[(t, t)] = 0
    max_comb = max(combinations.values())
    l1, l2 = list(types_by_name), list(types_by_name)
    world.random.shuffle(l2)
    rand_type_full = lambda _, b, e: world.random.choice(tuple(tt for tt in (l1 + ([e, e, e] if e else [])) if tt != b))
    if mods.is_permutation:
        perm = {t1: t2 for t1, t2 in itertools.zip_longest(l1, l2)}
        rand_type = lambda _t, _, __: perm[_t]
    else:
        rand_type = rand_type_full

    def roll(data: SpeciesEntry, pre: str | None):
        vanilla_data = by_name[data.species_name]
        t1, t2 = vanilla_data.types
        for try_ in range(2):
            if pre is not None:
                t1 = pre
            else:
                t1 = rand_type(t1, "", "")
            if dual_single == 1:
                t2 = t1
            elif dual_single == 2:
                t2 = rand_type(t2, t1, "")
                if t1 == t2:
                    t2 = rand_type_full("", t1, "")
            else:
                t2 = rand_type(t2, "", t1)
            if mods.is_usual_combinations and not try_:
                quot = combinations[(t1, t2)] / max_comb
                if world.random.random() > quot:
                    continue
            break
        data.types = (t1, t2)
        if mods.is_follow_evolutions:
            do_evos(data, world.random.choice(data.types))

    def do_evos(data: SpeciesEntry, pre: str | None):
        for evo_tup in data.evolutions:
            for evo_dat in evo_tup[2]:
                if not evo_dat.types[0]:
                    roll(evo_dat, pre)

    if mods.is_follow_evolutions:
        for spec in plandod_ts:
            dat = all_species[spec]
            do_evos(dat, world.random.choice(dat.types))
    for spec, dat in all_species.items():
        if not dat.types[0] and (not dat.form or dat.is_custom_form):
            roll(dat, None)
    for spec, dat in all_species.items():
        if dat.form and not dat.is_custom_form:
            base_data = by_id[dat.dex_number, 0]
            dat.types = base_data.types


def randomize_types_post_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                             by_id: dict[tuple[int, int], SpeciesEntry]):
    from ...data.pokemon.species import by_name
    from ...data.pokemon.types import by_name as types_by_name

    mods = world.options.randomize_types

    if not mods.is_randomize or (not mods.is_force_evolutions and
                                 (world.options.randomize_evolutions.is_common_type
                                  or world.options.randomize_evolutions.is_follow_type)):
        return

    plandod_ts = plando_types(world, all_species)
    dual_single = (mods.is_dual_only * 2 + mods.is_single_only) % 3
    combinations = {(t1, t2): 0 for t1 in types_by_name for t2 in types_by_name}
    for spec, dat in by_name.items():
        combinations[dat.types] += 1
        if dat.types[0] != dat.types[1]:
            combinations[dat.types[1], dat.types[0]] += 1
    if dual_single == 2:
        for t in types_by_name:
            combinations[(t, t)] = 0
    max_comb = max(combinations.values())
    l1, l2 = list(types_by_name), list(types_by_name)
    world.random.shuffle(l2)
    rand_type_full = lambda _, b, e: world.random.choice(tuple(tt for tt in (l1 + ([e, e, e] if e else [])) if tt != b))
    if mods.is_permutation:
        perm = {t1: t2 for t1, t2 in itertools.zip_longest(l1, l2)}
        rand_type = lambda _t, _, __: perm[_t]
    else:
        rand_type = rand_type_full

    def roll(data: SpeciesEntry, pre: tuple[str, ...]):
        if mods.is_force_evolutions and pre:
            data.types = pre
        else:
            vanilla_data = by_name[data.species_name]
            t1, t2 = vanilla_data.types
            for try_ in range(2):
                if pre:
                    t1 = world.random.choice(pre)
                else:
                    t1 = rand_type(t1, "", "")
                if dual_single == 1:
                    t2 = t1
                elif dual_single == 2:
                    t2 = rand_type(t2, t1, "")
                    if t1 == t2:
                        t2 = rand_type_full("", t1, "")
                else:
                    t2 = rand_type(t2, "", t1)
                if mods.is_usual_combinations and not try_:
                    quot = combinations[(t1, t2)] / max_comb
                    if world.random.random() > quot:
                        continue
                break
            data.types = (t1, t2)
        if mods.is_follow_evolutions or mods.is_force_evolutions:
            do_evos(data, data.types)

    def do_evos(data: SpeciesEntry, pre: tuple[str, ...]):
        for evo_tup in data.evolutions:
            for evo_dat in evo_tup[2]:
                if not evo_dat.types[0]:
                    roll(evo_dat, pre)

    if mods.is_follow_evolutions or mods.is_force_evolutions:
        for spec in plandod_ts:
            dat = all_species[spec]
            do_evos(dat, dat.types)
    for spec, dat in all_species.items():
        if not dat.types[0] and (not dat.form or dat.is_custom_form):
            roll(dat, ())
    for spec, dat in all_species.items():
        if dat.form and not dat.is_custom_form:
            base_data = by_id[(dat.dex_number, 0)]
            dat.types = base_data.types
