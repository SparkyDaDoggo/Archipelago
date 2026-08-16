from typing import Callable

from .. import EvolutionMethodData, ExtRulesTuple, AndExtRules as AND
from . import moves as move_tables, species
from ..locations.rules import *

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def has_item(name: str) -> ExtendedRule:
    return lambda state, world: state.has(name, world.player)


can_buy_item: dict[int, ExtendedRule] = {
    0x002E: has_access_mall_evo_items,  # Protein
    0x002F: has_access_mall_evo_items,  # Iron
    0x0030: has_access_mall_evo_items,  # Carbos
    80: has_access_twist_evo_items,  # Sun Stone
    81: has_access_twist_evo_items,  # Moon Stone
    82: has_access_castelia_evo_items,  # Fire Stone
    83: has_access_chargestone_evo_items,  # Thunder Stone
    84: has_access_castelia_evo_items,  # Water Stone
    85: has_access_castelia_evo_items,  # Leaf Stone
    107: has_access_r10_evo_items,  # Shiny Stone
    108: has_access_r10_evo_items,  # Dusk Stone
    109: has_access_r10_evo_items,  # Dawn Stone
    110: has_access_mall_evo_items,  # Oval Stone
    221: has_access_mall_evo_items,  # King's Rock
    226: has_access_undella_evo_items,  # Deep Sea Tooth
    227: has_access_undella_evo_items,  # Deep Sea Scale
    233: has_access_chargestone_evo_items,  # Metal Coat
    235: has_access_mall_evo_items,  # Dragon Scale
    252: has_access_undella_evo_items,  # Up-Grade
    321: has_access_mall_evo_items,  # Protector
    322: has_access_undella_evo_items,  # Electirizer
    323: has_access_undella_evo_items,  # Magmarizer
    324: has_access_undella_evo_items,  # Dubious Disc
    325: has_access_mall_evo_items,  # Reaper Cloth
    326: has_access_chasm_evo_items,  # Razor Claw
    327: has_access_chasm_evo_items,  # Razor Fang
    537: has_access_undella_evo_items,  # Prism Scale
}

stone_items = (80, 81, 82, 83, 84, 85, 107, 108, 109)
hold_items = (0x002E, 0x002F, 0x0030, 110, 221, 226, 227, 233, 235, 252, 321, 322, 323, 324, 325, 326, 327, 537)


def build_lvlup_ext_rule(divided: int) -> ExtendedRule:
    return lambda state, world: any(state.pokemon_bw_lvl[world.player][i] for i in range(divided, 21))


lvlup_ext_rule_cache = [build_lvlup_ext_rule(d) for d in range(21)]


def move_lvlup(value: int, spec: str, world: "PokemonBWWorld") -> ExtendedRule | ExtRulesTuple:
    # if move in levelup moveset, then level and access to move relearner
    for lvl_move in world.species_entries[spec].level_up_moves.level_up_moves:
        if world.move_entries[lvl_move[1]].id == value:
            return AND(lvlup_ext_rule_cache[lvl_move[0] // 5], has_access_move_relearner)
    # if move in tmhm moveset, then corresponding tmhm
    for tm_move in world.species_entries[spec].tm_hm_moves.tm_hm_moves:
        if world.move_entries[move_tables.tm_hm[tm_move].move].id == value:
            return has_item(tm_move)
    # cannot learn, bad plando, so just move relearner access
    return has_access_move_relearner


def party_member_lvlup(value: int, spec: str, world: "PokemonBWWorld") -> ExtendedRule:
    spec_name = species.by_id[value, 0]
    return has_item(spec_name)


EvoExtRule: type = Callable[[int, str, "PokemonBWWorld"], ExtendedRule | ExtRulesTuple | None]
specific_lvlup: EvoExtRule = lambda value, species, world: lvlup_ext_rule_cache[value // 5]
item_evo: EvoExtRule = lambda value, species, world: can_buy_item[value]
stats_lvlup: EvoExtRule = lambda value, species, world: AND(lvlup_ext_rule_cache[value // 5], has_access_mall_evo_items)

methods: dict[str, EvolutionMethodData] = {
    "Level up": EvolutionMethodData(4, True, specific_lvlup),
    "Stone": EvolutionMethodData(8, False, item_evo),
    "Stone male": EvolutionMethodData(17, False, item_evo),  # Repeatable encounters, including static, are ensured
    "Stone female": EvolutionMethodData(18, False, item_evo),  # Repeatable encounters, including static, are ensured
    "Friendship": EvolutionMethodData(1, False, lambda value, species, world: has_access_friendship_checker),  # Artificial logic because there's the friendship checker
    "Friendship (Day)": EvolutionMethodData(2, False, lambda value, species, world: has_access_friendship_checker),  # Only in plando
    "Friendship (Night)": EvolutionMethodData(3, False, lambda value, species, world: has_access_friendship_checker),  # Only in plando
    "Trade": EvolutionMethodData(5, False, None),  # Only in plando
    "Trade with item": EvolutionMethodData(6, False, item_evo),  # Only in plando
    "Trade Karrablast Shelmet": EvolutionMethodData(7, False, None),  # Only in plando
    "Magnetic area": EvolutionMethodData(25, False, lambda value, species, world: has_access_magnetic_area),
    "Unused area": EvolutionMethodData(28, False, lambda value, species, world: has_access_magnetic_area),  # Only in plando, unless used for custom area
    "Level up with move": EvolutionMethodData(21, False, move_lvlup),
    "Level up moss rock": EvolutionMethodData(26, False, lambda value, species, world: has_access_moss_rock),
    "Level up ice rock": EvolutionMethodData(27, False, lambda value, species, world: has_access_ice_rock),
    "Level up item day": EvolutionMethodData(19, False, item_evo),  # Always paired with night
    "Level up item night": EvolutionMethodData(20, False, item_evo),  # Always paired with day
    "Level up higher defense": EvolutionMethodData(11, True, stats_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up higher attack": EvolutionMethodData(9, True, stats_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up equal physical": EvolutionMethodData(10, True, stats_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up Silcoon": EvolutionMethodData(12, True, specific_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up Cascoon": EvolutionMethodData(13, True, specific_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up Ninjask": EvolutionMethodData(14, True, specific_lvlup),
    "Level up Shedinja": EvolutionMethodData(15, True, specific_lvlup),
    "Level up high beauty": EvolutionMethodData(16, False, None),  # Only in plando
    "Level up (female)": EvolutionMethodData(23, True, specific_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up (male)": EvolutionMethodData(24, True, specific_lvlup),  # Repeatable encounters, including static, are ensured
    "Level up with party member": EvolutionMethodData(22, False, party_member_lvlup),
}


paired_method_slots = {
    "_Level up item": 2,
    "_Level up split": 2,
    "_Level up PID": 2,
    "_Level up stats": 3,
}
