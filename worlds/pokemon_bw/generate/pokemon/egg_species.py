from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def set_value(data: SpeciesEntry, egg_spec: str):
    for form_data in data.all_forms:
        if form_data.egg_species is None:
            form_data.egg_species = egg_spec


def randomize_egg_species(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                          by_id: dict[tuple[int, int], SpeciesEntry]):

    mods = world.options.randomize_egg_species
    fix_mode = mods.is_fix_evolutions and len(mods.value) == 1

    all_plandod: list[SpeciesEntry] = []
    for species, plando_stat in world.options.stats_plando:
        if plando_stat.egg_species is not None:
            dat = all_species[species]
            dat.egg_species = plando_stat.egg_species
            if not dat.is_custom_form:
                set_value(dat, dat.egg_species)
            dat.write |= 0b1000000000
            all_plandod.append(dat)

    if not mods.value:
        return

    def roll(data: SpeciesEntry):
        chosen = world.random.randint(1, 649)
        for i in (*range(chosen, 650), *range(1, chosen)):
            chosen_data = by_id[i, 0]
            if mods.is_common_type and not any(t in data.types for t in chosen_data.types):
                continue
            if mods.is_base_stages_only and chosen_data.pre_evolutions:
                continue
            set_value(dat, chosen_data.species_name)
            break
        else:
            set_value(dat, data.species_name)
        if mods.is_follow_evolutions:
            do_evos(data, data.egg_species)

    def do_evos(data: SpeciesEntry, pre: str):
        for evo_tup in data.evolutions:
            if evo_tup.species.egg_species is None:
                dat.write |= 0b1000000000
                set_value(evo_tup.species, pre)
                do_evos(evo_tup.species, pre)
        if not fix_mode:
            for pre_evo_data in data.pre_evolutions:
                if pre_evo_data.egg_species is None:
                    dat.write |= 0b1000000000
                    set_value(pre_evo_data, pre)
                    do_evos(pre_evo_data, pre)

    if mods.is_follow_evolutions or fix_mode:
        for dat in all_plandod:
            do_evos(dat, dat.species_name)
    if fix_mode:
        for dat in all_species.values():
            if dat.egg_species is None and (not dat.form or dat.is_custom_form) and not dat.pre_evolutions:
                dat.write |= 0b1000000000
                set_value(dat, dat.species_name)
                do_evos(dat, dat.species_name)
        for dat in all_species.values():
            if dat.egg_species is None and (not dat.form or dat.is_custom_form):
                dat.write |= 0b1000000000
                set_value(dat, dat.species_name)
    else:
        for dat in all_species.values():
            dat.write |= 0b1000000000
            if dat.egg_species is None and not dat.form:
                roll(dat)
