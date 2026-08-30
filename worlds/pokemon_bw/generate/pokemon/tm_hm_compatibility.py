from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from .. import SpeciesEntry


def randomize_tm_hm_compat(world: "PokemonBWWorld", all_species: dict[str, "SpeciesEntry"]):
    from ...data.pokemon.moves import tm_hm
    from ...data import TMHMMovesetData

    mods = world.options.randomize_tm_hm_compatibility

    if not mods.is_randomize:
        for species, plando_stat in world.options.stats_plando:
            if plando_stat.tm_hm_compatibility:
                dat = all_species[species]
                dat.tm_hm_moves = TMHMMovesetData(dat.tm_hm_moves.tm_hm_moves | set(plando_stat.tm_hm_compatibility))
                dat.write |= 0b1000000
        return

    def roll(data: "SpeciesEntry", pre: set[str]):
        data.write |= 0b1000000
        new_set = set()
        for tm_name, tm_data in tm_hm.items():
            if mods.is_all_tms and not tm_data.is_HM:
                new_set.add(tm_name)
            elif mods.is_all_hms and tm_data.is_HM:
                new_set.add(tm_name)
            elif world.random.random() < 0.5:
                if not mods.is_match_types or world.move_entries[tm_data.move].type in (*data.types, "Normal"):
                    new_set.add(tm_name)
        new_set.update(pre)
        if data.species_name in world.options.stats_plando:
            new_set.update(world.options.stats_plando[data.species_name].tm_hm_compatibility)
        data.tm_hm_moves.tm_hm_moves.update(new_set)
        if mods.is_follow_evolutions:
            do_evos(data, data.tm_hm_moves.tm_hm_moves)

    def upgrade(data: "SpeciesEntry", pre: set[str]):
        if any(tm not in data.tm_hm_moves.tm_hm_moves for tm in pre):
            data.tm_hm_moves.tm_hm_moves.update(pre)
            do_evos(data, pre)

    def do_evos(data: "SpeciesEntry", pre: set[str]):
        for evo_tup in data.evolutions:
            evo_spec = evo_tup.species.by_form(data.form)
            if evo_spec.form and not evo_spec.is_custom_form:
                evo_spec = evo_spec.all_forms[0]
            if not evo_spec.write & 0b1000000:
                roll(evo_spec, pre)
            else:
                upgrade(evo_spec, pre)

    for dat in all_species.values():
        dat.tm_hm_moves = TMHMMovesetData(set())
    for nam, dat in all_species.items():
        if not dat.write & 0b1000000 and (not dat.form or dat.is_custom_form):
            roll(dat, set())
