from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def set_value(data: SpeciesEntry, egg_groups: tuple):
    for form_data in data.all_forms:
        if form_data.egg_groups is None:
            form_data.egg_groups = egg_groups


def randomize_egg_groups(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.egg_groups import groups

    mods = world.options.randomize_egg_groups

    all_plandod: list[SpeciesEntry] = []
    for species, plando_stat in world.options.stats_plando:
        if plando_stat.egg_groups:
            dat = all_species[species]
            dat.egg_groups = tuple(plando_stat.egg_groups) * (3 - len(plando_stat.egg_groups))
            if not dat.is_custom_form:
                set_value(dat, dat.egg_groups)
            dat.write |= 0b100000000
            all_plandod.append(dat)

    if not mods.is_randomize:
        return

    for dat in all_species.values():
        dat.write |= 0b100000000

    def roll_mono(pool: list[str]) -> tuple[str, str]:
        return (world.random.choice(pool),) * 2

    def roll_dual(pool: list[str]) -> tuple[str, str]:
        first = world.random.choice(pool)
        pool.remove(first)
        if not pool or first in ("Ditto", "Unknown"):
            return first, first
        else:
            return first, world.random.choice(pool)

    def roll_groups(data: SpeciesEntry) -> tuple[str, str]:
        pool = allowed.copy() if not mods.is_correlate_with_types \
            else list(g for g in allowed if (groups[g].compatible_types is None
                                             or any(t in data.types for t in groups[g].compatible_types)))
        if mods.is_mono_only and not mods.is_dual_only:
            return roll_mono(pool)
        elif mods.is_dual_only and not mods.is_mono_only:
            return roll_dual(pool)
        elif world.random.random() < 0.25:
            return roll_mono(pool)
        else:
            return roll_dual(pool)

    def roll(data: SpeciesEntry):
        chosen = roll_groups(data)
        set_value(data, chosen)
        if mods.is_follow_evolutions:
            do_evos(data, chosen)

    def do_evos(data: SpeciesEntry, pre: tuple[str, ...]):
        if (
            mods.is_allow_baby_stages and not data.pre_evolutions and data.evolutions
            and pre[0] == "Unknown" and world.random.random() < 0.25
        ):
            pre = roll_groups(data)
        for evo_tup in data.evolutions:
            if evo_tup.species.egg_groups is None:
                set_value(evo_tup.species, pre)
                do_evos(evo_tup.species, pre)
        for pre_evo_data in data.pre_evolutions:
            if pre_evo_data.egg_groups is None:
                new_pre = pre
                if (
                    mods.is_allow_baby_stages and not pre_evo_data.pre_evolutions
                    and pre[0] != "Unknown" and world.random.random() < 0.0625
                ):
                    new_pre = ("Unknown", "Unknown")
                set_value(pre_evo_data, new_pre)
                do_evos(pre_evo_data, pre)

    allowed = list(g for g, d in groups.items() if d.vanilla) if not mods.is_allow_custom_groups else list(groups)
    keep_ditto = True  # Needs assembly changes
    if keep_ditto:
        allowed.remove("Ditto")
        dat = all_species["Ditto"]
        set_value(dat, ("Ditto", "Ditto"))
        if mods.is_follow_evolutions:
            # do_evos(dat, ("Ditto", "Ditto"))
            do_evos(dat, roll_groups(dat))
    if mods.is_follow_evolutions:
        for dat in all_plandod:
            do_evos(dat, dat.egg_groups)
    for dat in all_species.values():
        if dat.egg_groups is None and not dat.form:
            roll(dat)
