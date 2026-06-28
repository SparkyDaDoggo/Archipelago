from typing import Callable, Any, TYPE_CHECKING

from .. import EvolutionMethodData, ExtendedRule
from . import movesets_level_up, movesets_tm_hm, moves as move_tables, species

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def has_item(name: str) -> ExtendedRule:
    return lambda state, world: state.has(name, world.player)


always_possible: ExtendedRule = lambda state, world: True
can_reach_magnetic_area: ExtendedRule = lambda state, world: state.can_reach_region("Chargestone Cave", world.player)
can_reach_moss_rock: ExtendedRule = lambda state, world: state.can_reach_region("Pinwheel Forest West", world.player)
can_reach_ice_rock: ExtendedRule = lambda state, world: state.can_reach_region("Twist Mountain", world.player)
can_reach_nacrene_city: ExtendedRule = lambda state, world: state.can_reach_region("Nacrene City", world.player)
can_reach_mistralton_city: ExtendedRule = lambda state, world: state.can_reach_region("Mistralton City", world.player)

can_buy_item_castelia: ExtendedRule = lambda state, world: state.can_reach_region("Castelia City", world.player)
can_get_item_chargestone: ExtendedRule = lambda state, world: state.can_reach_region("Chargestone Cave", world.player)
can_buy_item_twist: ExtendedRule = lambda state, world: state.can_reach_region("Twist Mountain", world.player)
can_buy_item_mall: ExtendedRule = lambda state, world: state.can_reach_region("Route 9", world.player)
can_get_item_r10: ExtendedRule = lambda state, world: state.can_reach_region("Route 10", world.player)
can_buy_item_undella: ExtendedRule = lambda state, world: state.can_reach_region("Undella Town", world.player)
can_get_item_chasm: ExtendedRule = lambda state, world: state.can_reach_region("Giant Chasm Entrance Cave", world.player)
can_buy_item: dict[int, ExtendedRule] = {
    0x002E: can_buy_item_mall,  # Protein
    0x002F: can_buy_item_mall,  # Iron
    0x0030: can_buy_item_mall,  # Carbos
    80: can_buy_item_twist,  # Sun Stone
    81: can_buy_item_twist,  # Moon Stone
    82: can_buy_item_castelia,  # Fire Stone
    83: can_get_item_chargestone,  # Thunder Stone
    84: can_buy_item_castelia,  # Water Stone
    85: can_buy_item_castelia,  # Leaf Stone
    107: can_get_item_r10,  # Shiny Stone
    108: can_get_item_r10,  # Dusk Stone
    109: can_get_item_r10,  # Dawn Stone
    110: can_buy_item_mall,  # Oval Stone
    221: can_buy_item_mall,  # King's Rock
    226: can_buy_item_undella,  # Deep Sea Tooth
    227: can_buy_item_undella,  # Deep Sea Scale
    233: can_get_item_chargestone,  # Metal Coat
    235: can_buy_item_mall,  # Dragon Scale
    252: can_buy_item_undella,  # Up-Grade
    321: can_buy_item_mall,  # Protector
    322: can_buy_item_undella,  # Electirizer
    323: can_buy_item_undella,  # Magmarizer
    324: can_buy_item_undella,  # Dubious Disc
    325: can_buy_item_mall,  # Reaper Cloth
    326: can_get_item_chasm,  # Razor Claw
    327: can_get_item_chasm,  # Razor Fang
    537: can_buy_item_undella,  # Prism Scale
}

stone_items = (80, 81, 82, 83, 84, 85, 107, 108, 109)
hold_items = (0x002E, 0x002F, 0x0030, 110, 221, 226, 227, 233, 235, 252, 321, 322, 323, 324, 325, 326, 327, 537)

in_vanilla_east: ExtendedRule = lambda state, world: (
    state.can_reach_region("Route 15", world.player)
    and not world.options.adjust_levels.is_wild
)
can_challenge_alder: ExtendedRule = lambda state, world: state.can_reach_region("N's Castle", world.player)
between_ghetsis_and_alder: ExtendedRule = lambda state, world: (
    in_vanilla_east(state, world)
    or can_challenge_alder(state, world)
)
is_in_appropriate_region: dict[int, ExtendedRule] = {  # Artificial logic so that you're not expected to evolve Larvesta in Striaton City
    0: always_possible,
    1: always_possible,
    2: always_possible,
    3: lambda state, world: state.can_reach_region("Pinwheel Forest Outside", world.player),
    4: lambda state, world: state.can_reach_region("Castelia City", world.player),
    5: lambda state, world: state.can_reach_region("Desert Resort", world.player),
    6: lambda state, world: state.can_reach_region("Undella Town", world.player) or  # Includes in_vanilla_east
                            state.can_reach_region("Mistralton Cave Inner", world.player) or
                            state.can_reach_region("Chargestone Cave", world.player),
    7: lambda state, world: state.can_reach_region("Route 13", world.player) or  # Includes in_vanilla_east
                            state.can_reach_region("Twist Mountain", world.player),
    8: lambda state, world: in_vanilla_east(state, world) or state.can_reach_region("Opelucid City", world.player),
    9: lambda state, world: in_vanilla_east(state, world) or state.can_reach_region("Victory Road", world.player),
    10: lambda state, world: in_vanilla_east(state, world) or state.can_reach_region("Pokémon League", world.player),
    11: between_ghetsis_and_alder,
    12: between_ghetsis_and_alder,
    13: between_ghetsis_and_alder,
    14: between_ghetsis_and_alder,
    15: can_challenge_alder,
    16: can_challenge_alder,
    17: can_challenge_alder,
    18: can_challenge_alder,
    19: can_challenge_alder,
    20: can_challenge_alder,
}


def stats_lvlup(value: int, spec: str, world: "PokemonBWWorld") -> ExtendedRule:
    return lambda state, world: (is_in_appropriate_region[value//5](state, world)
                                 and can_buy_item_mall(state, world))


def move_lvlup(value: int, spec: str, world: "PokemonBWWorld") -> ExtendedRule:  # TODO these evo rule builders need the world, because I need to check for the actual TM/HM moveset
    for lvl_move in world.species_entries[spec].level_up_moves.level_up_moves:
        if move_tables.by_name[lvl_move[1]].id == value:
            return lambda state, world: (is_in_appropriate_region[lvl_move[0]//5](state, world)
                                         and can_reach_mistralton_city(state, world))
    for tm_move in world.species_entries[spec].tm_hm_moves.tm_hm_moves:
        if move_tables.by_name[move_tables.tm_hm[tm_move].move].id == value:
            return has_item(tm_move)
    return can_reach_mistralton_city


appropriate_region: Callable[[int, str, "PokemonBWWorld"], ExtendedRule] = lambda value, species, world: is_in_appropriate_region[value//5]
item_evo: Callable[[int, str, "PokemonBWWorld"], ExtendedRule] = lambda value, species, world: can_buy_item[value]

methods: dict[str, EvolutionMethodData] = {
    "Level up": EvolutionMethodData(4, True, appropriate_region),
    "Stone": EvolutionMethodData(8, False, item_evo),
    "Stone male": EvolutionMethodData(17, False, item_evo),  # Repeatable encounters, including static, are ensured
    "Stone female": EvolutionMethodData(18, False, item_evo),  # Repeatable encounters, including static, are ensured
    "Friendship": EvolutionMethodData(1, False, lambda value, species, world: can_reach_nacrene_city),  # Artificial logic because there's the friendship checker
    "Friendship (Day)": EvolutionMethodData(2, False, lambda value, species, world: can_reach_nacrene_city),  # Only in plando
    "Friendship (Night)": EvolutionMethodData(3, False, lambda value, species, world: can_reach_nacrene_city),  # Only in plando
    "Trade": EvolutionMethodData(5, False, lambda value, species, world: always_possible),  # Only in plando
    "Trade with item": EvolutionMethodData(6, False, item_evo),  # Only in plando
    "Trade Karrablast Shelmet": EvolutionMethodData(7, False, lambda value, species, world: always_possible),  # Only in plando
    "Magnetic area": EvolutionMethodData(25, False, lambda value, species, world: can_reach_magnetic_area),
    "Unused area": EvolutionMethodData(28, False, lambda value, species, world: can_reach_magnetic_area),  # Only in plando, unless used for custom area
    "Level up with move": EvolutionMethodData(21, False, move_lvlup),
    "Level up moss rock": EvolutionMethodData(26, False, lambda value, species, world: can_reach_moss_rock),
    "Level up ice rock": EvolutionMethodData(27, False, lambda value, species, world: can_reach_ice_rock),
    "Level up item day": EvolutionMethodData(19, False, item_evo),  # Always paired with night
    "Level up item night": EvolutionMethodData(20, False, item_evo),  # Always paired with day
    "Level up higher defense": EvolutionMethodData(11, True, stats_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up higher attack": EvolutionMethodData(9, True, stats_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up equal physical": EvolutionMethodData(10, True, stats_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up Silcoon": EvolutionMethodData(12, True, appropriate_region),  # Repeatable encounters, including static, are ensured
    "Level up Cascoon": EvolutionMethodData(13, True, appropriate_region),  # Repeatable encounters, including static, are ensured
    "Level up Ninjask": EvolutionMethodData(14, True, appropriate_region),
    "Level up Shedinja": EvolutionMethodData(15, True, appropriate_region),
    "Level up high beauty": EvolutionMethodData(16, False, lambda value, species, world: always_possible),  # Only in plando
    "Level up (female)": EvolutionMethodData(23, True, appropriate_region),  # Repeatable encounters, including static, are ensured
    "Level up (male)": EvolutionMethodData(24, True, appropriate_region),  # Repeatable encounters, including static, are ensured
    "Level up with party member": EvolutionMethodData(22, False, lambda value, spec, world: has_item(species.by_id[value, 0])),
}


paired_method_slots = {
    "_Level up item": 2,
    "_Level up split": 2,
    "_Level up PID": 2,
    "_Level up stats": 3,
}
