from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def randomize_catch_rates(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.species import by_id
    from ...data.pokemon.pokedex import by_name as dex_by_name

    mods = world.options.randomize_catch_rates
    min_rate = world.options.stats_randomization_adjustments["Catch rates minimum"]
    max_rate = world.options.stats_randomization_adjustments["Catch rates maximum"]

    all_plandod = []
    for species, plando_stat in world.options.stats_plando:
        if plando_stat.catch_rate:
            actual_spec = by_id[(dex_by_name[species], 0)] if species not in all_species else species
            dat = all_species[actual_spec]
            dat.catch_rate = plando_stat.catch_rate
            dat.write |= 0b1000
            all_plandod.append(actual_spec)

    if not mods.is_shuffle:
        return

    possible = tuple(range(min_rate, max_rate)) if mods.is_randomize else tuple(r for r in (
        3, 5, 15, 25, 30, 35, 45, 50, 60, 65, 70, 75, 90, 100, 120, 125, 127, 130, 140, 145, 150, 155, 170, 180, 190,
        200, 205, 225, 231, 235, 255) if min_rate <= r <= max_rate)  # sorting is important!
    if not possible:
        possible = (min_rate, max_rate)

    def roll(data: SpeciesEntry, maximum: int):
        max_index = len(possible) - 1
        while possible[max_index] > maximum:
            max_index -= 1
        chosen = world.random.randrange(max_index + 1)
        if mods.is_correlate_with_base_stats:
            rate_cor = 1 - (possible[chosen] - min_rate) / (max_rate - min_rate)
            stats_cor = min(max((data.base_hp + data.base_attack + data.base_defense +
                                 data.base_sp_attack + data.base_sp_defense + data.base_speed) - 250, 0), 400) / 400
            if not rate_cor - 0.2 <= stats_cor <= rate_cor + 0.2:
                if stats_cor > rate_cor:
                    chosen = world.random.randrange(chosen + 1)
                else:
                    chosen = world.random.randrange(chosen, max_index + 1)
        data.catch_rate = possible[chosen]
        if mods.is_follow_evolutions:
            do_evos(data, possible[chosen])

    def downgrade(data: SpeciesEntry, maximum: int):
        if data.catch_rate > maximum:
            data.catch_rate = maximum
            do_evos(data, maximum)

    def do_evos(data: SpeciesEntry, maximum: int):
        for evo_tup in data.evolutions:
            for form in range(6):
                if (data.dex_number, form) not in by_id:
                    break
                evo_id_tup = (evo_tup[2], form)
                evo_species = by_id[evo_id_tup if evo_id_tup in by_id else (evo_tup[2], 0)]
                evo_dat = all_species[evo_species]
                if form and not evo_dat.is_custom_form:
                    break
                if not evo_dat.catch_rate:
                    roll(evo_dat, maximum)
                elif evo_dat.evo_line is None or data.dex_number not in evo_dat.evo_line:
                    downgrade(evo_dat, maximum)

    for spec in all_plandod:
        dat = all_species[spec]
        do_evos(dat, dat.catch_rate)
    for dat in all_species.values():
        dat.catch_rate = 0
        dat.write |= 0b1000
    for dat in all_species.values():
        if not dat.catch_rate and (not dat.form or dat.is_custom_form):
            roll(dat, max_rate)
    for spec, dat in all_species.items():
        if dat.form and not dat.is_custom_form:
            base_data = all_species[by_id[(dat.dex_number, 0)]]
            dat.catch_rate = base_data.catch_rate
