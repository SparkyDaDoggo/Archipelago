
from typing import TYPE_CHECKING
from .. import SpeciesChecklist, CopyChecklist
import logging

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from .. import SpeciesChecklist


def generate_wild(world: "PokemonBWWorld", species_checklist: SpeciesChecklist):
    from ...data.plando.encounter_maps import maps, multiple_seasons
    from ...data.locations.encounters.regions import region_list

    method_abbr = {
        "Grass": "G",
        "Dark grass": "DG",
        "Rustling grass": "RG",
        "Surfing": "S",
        "Surfing rippling": "SR",
        "Fishing": "F",
        "Fishing rippling": "FR",
    }
    season_index = {
        "": 0,
        "(Spring) ": 0,
        "(Summer) ": 1,
        "(Autumn) ": 2,
        "(Winter) ": 3,
    }
    method_shifting = {
        "Grass": (0, 11),
        "Dark grass": (12, 23),
        "Rustling grass": (24, 35),
        "Surfing": (36, 40),
        "Surfing rippling": (41, 45),
        "Fishing": (46, 50),
        "Fishing rippling": (51, 55),
    }

    for plando in world.options.encounter_plando:
        if len(plando.species) == 1:
            species = plando.species[0]
        else:
            species = world.random.choice(plando.species)
        if species.casefold() == "none":
            continue
        species_data = world.species_entries[species]
        map_abbr, file_index = maps[plando.map]
        if not plando.seasons:
            if plando.map in multiple_seasons:
                seasons = ["(Spring) ", "(Summer) ", "(Autumn) ", "(Winter) "]
            else:
                seasons = [""]
        else:
            seasons = [f"({season}) " for season in plando.seasons]
        for season in seasons:
            season_id = season_index[season]
            method = method_abbr[plando.method]
            region = f"{map_abbr} {season}- {method}"
            er_data = region_list[map_abbr]
            if (
                (season_id == 0 and method not in (er_data.methods + er_data.spring_methods))
                or (season_id == 1 and method not in er_data.summer_methods)
                or (season_id == 2 and method not in er_data.autumn_methods)
                or (season_id == 3 and method not in er_data.winter_methods)
            ):
                logging.warning(f"Player {world.player_name} defined an Encounter Plando on a non-existent slot "
                                f"({region}).")
                continue
            slots = plando.slots or (
                list(range(12))
                if plando.method in ("Grass", "Dark grass", "Rustling grass")
                else list(range(5))
            )
            for slot in slots:
                slot_in_file = method_shifting[plando.method][0] + slot
                entry = world.wild_encounter[file_index, season_id, slot_in_file]
                entry.species_id = (species_data.dex_number, species_data.form)
                entry.write |= 2
                if entry.region in world.regions:
                    # Seasonal encounter regions (while vanilla seasons) were removed in a previous step
                    species_checklist.check(species_data)
