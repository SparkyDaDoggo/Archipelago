from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


# TODO prevent species with gender-dependent evos or gendersanity locations from getting ratios > 239 or < 15


def set_value(data: SpeciesEntry, ratio: int):
    data.gender_ratio = ratio
    if not data.is_custom_form:
        for form_data in data.all_forms:
            if not form_data.is_custom_form:
                form_data.gender_ratio = data.gender_ratio


def randomize_stats_pre_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):

    mods = world.options.randomize_gender_ratio

    if not mods.is_shuffle:
        for plando_name, plando_stat in world.options.stats_plando:
            data = all_species[plando_name]
            set_value(data, plando_stat.gender_ratio if plando_stat.gender_ratio != -1 else data.gender_ratio)
        return

    for data in all_species.values():
        data.gender_ratio = -1
        data.write |= 0b10000000000

    if mods.is_follow_evolutions:  # Do later in case of evo rando, which can work with -1 as gender ratio
        return

    max_ratio = world.options.stats_randomization_adjustments["Gender ratio maximum"]
    min_ratio = world.options.stats_randomization_adjustments["Gender ratio minimum"]
    possible = tuple(range(min_ratio, max_ratio) if mods.is_randomize
                     else (i for i in (0, 31, 63, 127, 191, 254)
                           if min_ratio <= i <= max_ratio)) + ((255,) if not mods.is_no_unknown_gender else ())

    for data in all_species.values():
        if data.gender_ratio != -1:
            continue
        if data.form and not data.is_custom_form:
            continue
        if mods.is_keep_fixed and data.gender_ratio_copy in (0, 254, 255):
            chosen = data.gender_ratio_copy
        else:
            chosen = world.random.choice(possible)
        set_value(data, chosen)


def randomize_stats_post_evo(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):

    mods = world.options.randomize_gender_ratio

    if not mods.is_shuffle or not mods.is_follow_evolutions:
        return

    max_ratio = world.options.stats_randomization_adjustments["Gender ratio maximum"]
    min_ratio = world.options.stats_randomization_adjustments["Gender ratio minimum"]
    possible = tuple(range(min_ratio, max_ratio) if mods.is_randomize
                     else (i for i in (0, 31, 63, 127, 191, 254)
                           if min_ratio <= i <= max_ratio)) + ((255,) if not mods.is_no_unknown_gender else ())

    def roll(data: SpeciesEntry):
        if mods.is_keep_fixed and data.gender_ratio_copy in (0, 254, 255):
            chosen = data.gender_ratio_copy
        else:
            chosen = world.random.choice(possible)
        set_value(data, chosen)
        do_evos(data, chosen)

    def do_evos(data: SpeciesEntry, this: int):
        for evo_tup in data.evolutions:
            evo_spec = evo_tup.species.by_form(data.form)
            set_value(evo_spec, this)
            do_evos(evo_spec, this)
        for pre in data.pre_evolutions:
            set_value(pre, this)
            do_evos(pre, this)

    for dat in all_species.values():
        if dat.gender_ratio != -1 and (not dat.form or dat.is_custom_form):
            roll(dat)
