from typing import TYPE_CHECKING

from ...locations import PokemonBWLocation
from BaseClasses import ItemClassification
from ...items import PokemonBWItem

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def create(world: "PokemonBWWorld") -> None:

    all_goals = world.options.goal.combined or [world.options.goal.current_key]
    needed_goals = []
    possible_goals = {
        "ghetsis": ("[Event] Defeating Ghetsis", ),
        "champion": ("[Event] Defeating champ Alder", ),
        "cynthia": ("[Event] Defeating Cynthia", ),
        "cobalion": ("[Event] Encounter Cobalion", ),
        "tmhm_hunt": ("[Event] Verifying TMs/HMs Castelia", ),
        # "regional_pokedex": (),
        # "national_pokedex": (),
        # "custom_pokedex": (),
        "seven_sages_hunt": (
            "[Event] Catching sage Rood",
            "[Event] Catching sage Gorm",
            "[Event] Catching sage Ryoku",
            "[Event] Catching sage Zinzolin",
            "[Event] Catching sage Bronius",
            "[Event] Catching sage Giallo",
            "[Event] Defeating Ghetsis",
        ),
        "legendary_hunt": (
            "[Event] Encounter Virizion",
            "[Event] Encounter Victini",
            "[Event] Encounter Volcarona",
            "[Event] Encounter Cobalion",
            "[Event] Encounter Kyurem",
            "[Event] Encounter Terrakion",
            "[Event] Encounter Reshiram/Zekrom",
        ),
    }
    for goal in all_goals:
        if goal == "pokemon_master":
            needed_goals += (g for gevents in possible_goals.values() for g in gevents)
        elif goal in possible_goals:
            needed_goals += possible_goals[goal]
        else:
            raise Exception(f"Bad goal option: {goal}")
    world.multiworld.completion_condition[world.player] = lambda state: state.has_all(needed_goals, world.player)
