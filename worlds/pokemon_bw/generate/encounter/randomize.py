from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def create_encounter(world: "PokemonBWWorld") -> None:
    from . import wild, checklist, static, plando, trainers, levels
    from .. import EncounterEntry, TrainerPokemonEntry
    from ...data.locations.encounters import slots
    from ...data.locations.encounters import regions as enc_regions
    from ...data.trainers.pokemon import table as trainer_pokemon_table

    versioned_species = (
        (lambda d: d.species_white)
        if world.options.version == "white"
        else (lambda d: d.species_black)
    )

    world.wild_encounter = {
        data.file_index: EncounterEntry(versioned_species(data), enc_regions.region_tup_by_file_tup(data.file_index),
                                        data.file_index, 0, data.min_level, data.max_level).build_region()
        for data in slots.table
    }
    world.trainer_teams = [
        TrainerPokemonEntry(data.trainer_id, data.team_number, data.species, data.level, 0)
        for data in trainer_pokemon_table
    ]

    levels.adjust_and_modify(world)

    species_checklist = checklist.get_species_checklist(world)
    copy_checklist = checklist.get_copy_checklist(world)

    # Static and trade encounter generation also remove and add species from/to checklist
    plando.generate_wild(world, species_checklist)  # only removes species
    world.trade_encounter = static.generate_trade_encounters(world, species_checklist)  # removes and adds species
    world.static_encounter = static.generate_static_encounters(world, species_checklist)  # only removes species
    wild.generate_wild_encounters(world, species_checklist, copy_checklist)  # only removes species

    trainers.generate_trainer_teams(world)
