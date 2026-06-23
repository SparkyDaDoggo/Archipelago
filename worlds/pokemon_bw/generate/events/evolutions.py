from typing import TYPE_CHECKING, Callable

from BaseClasses import ItemClassification, CollectionState

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from ...data import EvolutionMethodData, ExtendedRule
    from .. import SpeciesEntry


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]) -> None:

    if not world.options.modify_logic.is_consider_evos:
        return

    from ...data.pokemon import species, evolution_methods
    from ...locations import PokemonBWLocation
    from ...items import PokemonBWItem
    # Keywords to describe var names:
    # "dex" is the pokédex number
    # "form" is the form number
    # "id" is the combination of dex and form
    # "name" is the name shown in the pokédex
    # "species" is the pokédex name that includes a description of the form
    # "speciesdata" are the values in species.by_name
    # "evodata" is the evolution tuple of a species in species.by_name
    #           it consists of (evo_method, evo_value, evo_species)
    # "evoid" is the combination of species and index of one of its evodata
    # "base" (prefix) is the to-be-evolved species
    # "evo" (prefix) is the result of evolving the base species

    region: "Region" = world.regions["Evolutions"]

    def get_rule(f_evodata: tuple[str, int, int], f_base_species: str) -> Callable[[CollectionState], bool]:
        # helper function to prevent lambdas in for loops
        method: "EvolutionMethodData" = evolution_methods.methods[f_evodata[0]]
        ext_rule: "ExtendedRule" = method.rule(f_evodata[1], f_base_species)
        return lambda state: ext_rule(state, world) and state.has(f_base_species, world.player)

    # Dict instead of set to make it deterministic
    noted_evoid_set: dict[tuple[str, int], None] = {}
    current_evoid_set: dict[tuple[str, int], None] = {}
    next_evoid_set: dict[tuple[str, int], None] = {}
    # Populate initial set by adding all evolutions of every (already) catchable species
    for base_species, base_speciesdata in catchable_species_data.items():
        for evoid_index in range(len(base_speciesdata.evolutions)):
            evoid = (base_species, evoid_index)
            current_evoid_set[evoid] = None
            noted_evoid_set[evoid] = None

    # Iterate as long as it has been signaled that there is something new to check
    check_next = True
    while check_next:
        check_next = False
        # Iterate through all currently to-be-checked evoids
        for current_evoid in current_evoid_set:
            current_base_data = world.species_entries[current_evoid[0]]
            current_evodata = current_base_data.evolutions[current_evoid[1]]
            # Level up item night is always paired with Level up item day
            # and always has the same evolved species and item, so skip if it's that method
            if current_evodata[0] == "Level up item night":
                continue
            # Check for the evolution being possible if it requires a party member
            if current_evodata[0] == "Level up with party member":
                # Go through catchable and check whether the required team member
                # (or any of its forms) is already catchable
                for catchable_species, catchable_data in catchable_species_data.items():
                    # If evolution possible, jump to creating event
                    if catchable_data.dex_number == current_evodata[1]:
                        break
                else:
                    # If required team member not found, add this evoid to next iteration and skip adding event
                    next_evoid_set[current_evoid] = None
                    continue
            current_evoname = species.by_id[(current_evodata[2], current_base_data.form)]
            # Creating event
            location_name = f"Evolving {current_evoid[0]} #{current_evoid[1]+1}"
            location = PokemonBWLocation(world.player, location_name, None, region)
            item = PokemonBWItem(current_evoname, ItemClassification.progression, None, world.player)
            location.place_locked_item(item)
            location.show_in_spoiler = False
            location.access_rule = get_rule(current_evodata, current_evoid[0])
            region.locations.append(location)
            # Add the evolution to catchable
            evo_speciesdata = world.species_entries[current_evoname]
            catchable_species_data[current_evoname] = evo_speciesdata
            # Add evo's evodatas to noted and next evodatas
            check_next = True
            for evo_evodata_index in range(len(evo_speciesdata.evolutions)):
                evo_evoid = (current_evoname, evo_evodata_index)
                if evo_evoid not in noted_evoid_set:
                    noted_evoid_set[evo_evoid] = None
                    next_evoid_set[evo_evoid] = None
        if check_next:
            current_evoid_set = next_evoid_set
            next_evoid_set = {}
