from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def randomize_catch_rates(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                          by_id: dict[tuple[int, int], SpeciesEntry]):

    mods = world.options.randomize_catch_rates
    min_rate = world.options.stats_randomization_adjustments["Catch rates minimum"]
    max_rate = world.options.stats_randomization_adjustments["Catch rates maximum"]

    if mods.is_shuffle:
        for dat in all_species.values():
            dat.catch_rate = 0
            dat.write |= 0b1000

    all_plandod: list[SpeciesEntry] = []
    for species, plando_stat in world.options.stats_plando:
        if plando_stat.catch_rate:
            dat = all_species[species]
            dat.catch_rate = plando_stat.catch_rate
            dat.write |= 0b1000
            all_plandod.append(dat)

    if not mods.is_shuffle:
        return

    possible = tuple(range(min_rate, max_rate+1)) if mods.is_randomize else tuple(r for r in (
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
            stats_cor = min(max(sum(data.base_stats) - 250, 0), 400) / 400
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
            for evo_data in evo_tup[2]:
                if not evo_data.catch_rate:
                    roll(evo_data, maximum)
                else:
                    downgrade(evo_data, maximum)

    if mods.is_follow_evolutions:
        for dat in all_plandod:
            do_evos(dat, dat.catch_rate)
    for dat in all_species.values():
        if not dat.catch_rate and (not dat.form or dat.is_custom_form):
            roll(dat, max_rate)
    for dat in all_species.values():
        if dat.form and not dat.is_custom_form:
            base_data = by_id[dat.dex_number, 0]
            dat.catch_rate = base_data.catch_rate
