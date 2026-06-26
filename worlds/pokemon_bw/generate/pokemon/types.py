import itertools
from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def plando_types(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]) -> list[str]:
    from ...data.pokemon.pokedex import by_name as dex_by_name
    from ...data.pokemon.species import by_id

    all_plandod = []

    for species, plando_stat in world.options.stats_plando:
        if plando_stat.types:
            actual_spec = by_id[(dex_by_name[species], 0)] if species not in all_species else species
            data = all_species[actual_spec]
            data.write |= 0b100000
            data.type_1, data.type_2 = plando_stat.types * (3 - len(plando_stat.types))
            all_plandod.append(actual_spec)

    return all_plandod


def randomize_types_pre_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.species import by_name, by_id
    from ...data.pokemon.types import by_name as types_by_name

    mods = world.options.randomize_types

    if not mods.is_randomize:
        plando_types(world, all_species)
        return

    for dat in all_species.values():
        dat.type_1, dat.type_2 = "", ""
        dat.write |= 0b100000

    if mods.is_force_evolutions or not (world.options.randomize_evolutions.is_common_type
                                        or world.options.randomize_evolutions.is_follow_type):
        return

    plandod_ts = plando_types(world, all_species)
    dual_single = (mods.is_dual_only * 2 + mods.is_single_only) % 3
    combinations = {(t1, t2): 0 for t1 in types_by_name for t2 in types_by_name}
    for spec, dat in by_name.items():
        combinations[(dat.type_1, dat.type_2)] += 1
        combinations[(dat.type_2, dat.type_1)] += 1
    if dual_single == 2:
        for t in types_by_name:
            combinations[(t, t)] = 0
    max_comb = max(combinations.values())
    l1, l2 = list(types_by_name), list(types_by_name)
    world.random.shuffle(l2)
    rand_type_full = lambda _, b, e: world.random.choice(tuple(tt for tt in (l1 + ([e, e, e] if e else [])) if tt != b))
    if mods.is_permutation:
        perm = {t1: t2 for t1, t2 in itertools.zip_longest(l1, l2)}
        rand_type = lambda t, _, __: perm[t]
    else:
        rand_type = rand_type_full

    def roll(species: str, data: SpeciesEntry, pre: str | None):
        vanilla_data = by_name[species]
        t1 = vanilla_data.type_1
        t2 = vanilla_data.type_2
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
        data.type_1, data.type_2 = t1, t2
        if mods.is_follow_evolutions:
            do_evos(data, world.random.choice((t1, t2)))

    def do_evos(data: SpeciesEntry, pre: str | None):
        for evo_tup in data.evolutions:
            for form in range(6):
                if (data.dex_number, form) not in by_id:
                    break
                evo_id_tup = (evo_tup[2], form)
                evo_species = by_id[evo_id_tup if evo_id_tup in by_id else (evo_tup[2], 0)]
                evo_dat = all_species[evo_species]
                if form and not evo_dat.is_custom_form:
                    break
                if not evo_dat.type_1:
                    roll(evo_species, evo_dat, pre)

    if mods.is_follow_evolutions:
        for spec in plandod_ts:
            dat = all_species[spec]
            do_evos(dat, world.random.choice((dat.type_1, dat.type_2)))
    for spec, dat in all_species.items():
        if not dat.type_1 and (not dat.form or dat.is_custom_form):
            roll(spec, dat, None)
    for spec, dat in all_species.items():
        if dat.form and not dat.is_custom_form:
            base_data = all_species[by_id[(dat.dex_number, 0)]]
            dat.type_1, dat.type_2 = base_data.type_1, base_data.type_2


def randomize_types_post_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.species import by_name, by_id
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
        combinations[(dat.type_1, dat.type_2)] += 1
        combinations[(dat.type_2, dat.type_1)] += 1
    if dual_single == 2:
        for t in types_by_name:
            combinations[(t, t)] = 0
    max_comb = max(combinations.values())
    l1, l2 = list(types_by_name), list(types_by_name)
    world.random.shuffle(l2)
    rand_type_full = lambda _, b, e: world.random.choice(tuple(tt for tt in (l1 + ([e, e, e] if e else [])) if tt != b))
    if mods.is_permutation:
        perm = {t1: t2 for t1, t2 in itertools.zip_longest(l1, l2)}
        rand_type = lambda t, _, __: perm[t]
    else:
        rand_type = rand_type_full

    def roll(species: str, data: SpeciesEntry, pre: tuple[str, ...]):
        if mods.is_force_evolutions and pre:
            data.type_1, data.type_2 = pre
        else:
            vanilla_data = by_name[species]
            t1 = vanilla_data.type_1
            t2 = vanilla_data.type_2
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
            data.type_1, data.type_2 = t1, t2
        if mods.is_follow_evolutions or mods.is_force_evolutions:
            do_evos(data, (data.type_1, data.type_2))

    def do_evos(data: SpeciesEntry, pre: tuple[str, ...]):
        for evo_tup in data.evolutions:
            for form in range(6):
                if (data.dex_number, form) not in by_id:
                    break
                evo_id_tup = (evo_tup[2], form)
                evo_species = by_id[evo_id_tup if evo_id_tup in by_id else (evo_tup[2], 0)]
                evo_dat = all_species[evo_species]
                if form and not evo_dat.is_custom_form:
                    break
                if not evo_dat.type_1:
                    roll(evo_species, evo_dat, pre)

    if mods.is_follow_evolutions or mods.is_force_evolutions:
        for spec in plandod_ts:
            dat = all_species[spec]
            do_evos(dat, (dat.type_1, dat.type_2))
    for spec, dat in all_species.items():
        if not dat.type_1 and (not dat.form or dat.is_custom_form):
            roll(spec, dat, ())
    for spec, dat in all_species.items():
        if dat.form and not dat.is_custom_form:
            base_data = all_species[by_id[(dat.dex_number, 0)]]
            dat.type_1, dat.type_2 = base_data.type_1, base_data.type_2
