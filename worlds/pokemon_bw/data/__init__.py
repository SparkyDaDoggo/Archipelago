from typing import NamedTuple, Callable, Literal, TYPE_CHECKING, TypeVar, Any, Union, Self

from BaseClasses import ItemClassification, LocationProgressType, CollectionState

if not TYPE_CHECKING:
    AccessRule: type = Any
    ExtendedRule: type = Any
    ClassificationMethod: type = Any
    ProgressTypeMethod: type = Any
    InclusionRule: type = Any
else:
    from .. import PokemonBWWorld
    from ..generate import SpeciesEntry
    AccessRule: type = Callable[[CollectionState], bool]
    ExtendedRule: type = Callable[[CollectionState, PokemonBWWorld], bool]
    ClassificationMethod: type = Callable[[PokemonBWWorld, str], ItemClassification]
    ProgressTypeMethod: type = Callable[[PokemonBWWorld], LocationProgressType]
    InclusionRule: type = Callable[[PokemonBWWorld], bool]

T = TypeVar("T")
U = TypeVar("U")


class ItemData(NamedTuple):
    item_id: int
    classification: ClassificationMethod


class BadgeItemData(NamedTuple):
    item_id: int
    bit: int
    classification: ClassificationMethod


class SeasonItemData(NamedTuple):
    item_id: int
    flag_id: int
    var_value: int
    classification: ClassificationMethod


class ExtRulesTuple(tuple[ExtendedRule | InclusionRule | Self, ...]):

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, args)

    def resolve(self: Self | ExtendedRule, world: "PokemonBWWorld") -> AccessRule:
        if isinstance(self, ExtRulesTuple):
            return self.resolve(world)
        return lambda state: self(state, world)


class AndExtRules(ExtRulesTuple):

    def resolve(self, world: "PokemonBWWorld") -> AccessRule:
        resolved = tuple(ExtRulesTuple.resolve(exrule, world) for exrule in self)

        def f(state: CollectionState) -> bool:
            for rule in resolved:
                if not rule(state):
                    return False
            return True
        return f


class OrExtRules(ExtRulesTuple):

    def resolve(self, world: "PokemonBWWorld") -> AccessRule:
        resolved = tuple(ExtRulesTuple.resolve(exrule, world) for exrule in self)

        def f(state: CollectionState) -> bool:
            for rule in resolved:
                if rule(state):
                    return True
            return False
        return f


class IfExtRules(ExtRulesTuple):

    def resolve(self, world: "PokemonBWWorld") -> AccessRule:
        return world.rules_dict[None] if not self[0](world) else ExtRulesTuple.resolve(self[1], world)


class RulesDict(dict[ExtendedRule | ExtRulesTuple | None, AccessRule]):

    def __init__(self, world: "PokemonBWWorld" = None):
        super().__init__()
        self.world = world
        self[None] = lambda state: True

    def get_or_add(self, item: ExtendedRule | ExtRulesTuple | None) -> AccessRule:
        if item not in self:
            self[item] = ExtRulesTuple.resolve(item, self.world)
        return self[item]


class FlagLocationData(NamedTuple):
    # flags begin at 0x23bf28 (B) or 0x23bf48 (W)
    flag_id: int
    progress_type: ProgressTypeMethod
    region: str
    inclusion_rule: InclusionRule | None
    rule: ExtendedRule | ExtRulesTuple | None


class TMLocationData(NamedTuple):
    flag_id: int
    progress_type: ProgressTypeMethod
    region: str
    inclusion_rule: InclusionRule | None
    hm_rule: Callable[[str], bool] | None
    rule: ExtendedRule | ExtRulesTuple | None


class DexLocationData(NamedTuple):
    # caught flags are stored at 0x23D1B4 (B) or 0x23D1D4 (W)
    dex_number: int
    ut_alias: str | None = None


class TrainerLocationData(NamedTuple):
    trainer_ids: int | tuple[int, ...]
    region: str
    # common_script: bool
    inclusion_rule: InclusionRule | None
    rule: ExtendedRule | ExtRulesTuple | None


class VisitLocationData(NamedTuple):
    map_id: int
    regions: tuple[str, ...]
    inclusion_rule: InclusionRule | None


class EncounterData(NamedTuple):
    species_black: tuple[int, int]
    species_white: tuple[int, int]
    file_index: tuple[int, int, int]
    min_level: int
    max_level: int


class StaticEncounterData(NamedTuple):
    # (dex number, form)
    species_black: tuple[int, int]
    species_white: tuple[int, int]
    encounter_region: str
    inclusion_rule: InclusionRule | None
    access_rule: ExtendedRule | None


class TradeEncounterData(NamedTuple):
    # (dex number, form)
    species_black: tuple[int, int]
    species_white: tuple[int, int]
    # only dex number
    wanted_black: int
    wanted_white: int
    encounter_region: str


class TrainerData(NamedTuple):
    id: int
    name: str
    region: str
    trainer_class: str
    pokemon_count: int
    items: tuple[str | None, str | None, str | None, str | None] | None  # Will be filled in the future
    held_items: bool
    unique_moves: bool
    pokemon_entry_length: int
    gym: tuple[str, str, bool] | None
    """(City name (without the "City") or "League", vanilla type, is leader)"""
    rival: int
    """0 no rival, 1-3 Bianca, 4-6 Cheren, 7 N
    rival order is Snivy/Tepig/Oshawott chosen by player"""
    do_not_adjust: bool = False
    logic_inc_rule: InclusionRule | None = None
    access_rule: ExtendedRule | ExtRulesTuple | None = None
    # early: bool
    # nearby_maps: tuple[int, ...]


class TrainerPokemonData(NamedTuple):
    trainer_id: int
    team_number: int
    ivs: int
    gender: int
    ability: int
    level: int
    nature: int
    species: str
    # held_item: str | None
    # moves: tuple[str, str, str, str] | None


class RegionData(NamedTuple):
    type: Literal["City", "Route", "Dungeon", "Gate", "Interior", "Bridge", "Virtual"]
    map_id: int  # -1 for virtual maps
    has_encounters: bool  # referring to map id
    full_map: bool = True  # Not a full map are e.g. Route 1 East/West


class RegionConnectionData(NamedTuple):
    region_1: str
    region_2: str
    type: Literal[
        "Door", "Gate", "Trees", "Stairs", "Cave", "Open transition", "Warp",
        "Adjacent maps",
        "Elevator", "Quicksand",
        "Other script",
        "Virtual"
    ]
    """
    - Actual warps
    - Really just walking from one map to another, never shuffled
    - Controlled by a script, but can be shuffled amongst each other
    - Controlled by a script, never shuffled
    - Between non-full maps or with virtual maps involved, never shuffled
    """
    warp_id: tuple[int | tuple[int, ...], int | tuple[int, ...]] | tuple  #
    """
    empty tuple for non-warp connections
    tuple instead of int for places where a long warp is split into multiple ones, first ID is the preferred destination
    """
    entrance_name: str | None
    """
    "##" will be replaced with with r1, "#2#" with r2
    None is replaced by "r1 -> r2" (AP default)
    """
    rule: ExtendedRule | ExtRulesTuple | None = None
    rule_2: ExtendedRule | ExtRulesTuple | None | Literal[False] = False  # for r2->r1 connection, False means copy the rules above
    one_way: bool = False  # r1->r2 only
    fixed: bool = False  # flag for warp/elevator connections that should not be shuffled


class EncounterRegionData(NamedTuple):
    file: int
    seasons: bool
    methods: tuple[str, ...] = ()
    spring_methods: tuple[str, ...] = ()
    summer_methods: tuple[str, ...] = ()
    autumn_methods: tuple[str, ...] = ()
    winter_methods: tuple[str, ...] = ()


class EncounterRegionConnectionData(NamedTuple):
    entering_region: tuple[str, str, str]
    exiting_regions: tuple[str, ...]

    def build_name(self) -> str:
        season = '' if not self.entering_region[1] else f" ({self.entering_region[1]})"
        return f"{self.entering_region[0]}{season} - {self.entering_region[2]}"


class EventData(NamedTuple):
    name: str
    region: str
    inclusion_rule: InclusionRule | None
    access_rule: ExtendedRule | ExtRulesTuple | None


class SpeciesData(NamedTuple):
    dex_name: str
    species_name: str | None
    dex_number: int
    form: int
    types: tuple[str, str]
    base_stats: tuple[int, int, int, int, int, int]
    catch_rate: int
    gender_ratio: int
    exp_curve: int
    # starts with 1 for base evolutions
    evolution_stage: int
    # (primary, secondary, hidden)
    abilities: tuple[str, str, str]
    # tuple(method, parameter, evolve into)
    evolutions: list[tuple[str, int, str]]
    # forms that cave custom stats
    is_custom_form: bool = False
    custom_form_file: int = 0


class LevelUpMovesetData(NamedTuple):
    # tuple(level, move name)
    level_up_moves: list[tuple[int, str]]


class TMHMMovesetData(NamedTuple):
    # TM number (internal order is TM01-95 HM01-06)
    tm_hm_moves: set[str]


class MoveData(NamedTuple):
    id: int
    type: str
    category: Literal["Physical", "Special", "Status"]
    power: int
    accuracy: int
    pp: int
    # (Number of positive effects) - (Number of negative effects)
    # effects_difference: int


class TMHMData(NamedTuple):
    move: str
    is_HM: bool
    index: int


class EvolutionMethodData(NamedTuple):
    id: int
    has_level_value: bool
    priority: int
    allow_multiple: bool  # multiple of that method per species
    # Takes value from evolution data and returns the access rule for that evolution
    rule: Callable[[int, "SpeciesEntry", "PokemonBWWorld"], ExtendedRule | ExtRulesTuple | None] | None


class TypeData(NamedTuple):
    id: int


class EggGroupData(NamedTuple):
    id: int
    vanilla: bool
    compatible_types: tuple[str, ...] | None


class WildAdjustmentData(NamedTuple):
    calculation: Callable[[int], int]
    file: int
    season: int
    method: Literal[
        "grass", "dark grass", "rustling grass", "surfing", "surfing rippling", "fishing", "fishing rippling"
    ]


class TrainerAdjustmentData(NamedTuple):
    calculation: Callable[[int], int]
    trainer_id: int


class TextData(NamedTuple):
    credit: str
    section: Literal["story", "system"]
    file: int
    block: int
    entry: int
    text: str


AnyItemData: type = Union[ItemData, BadgeItemData, SeasonItemData]
AnyLocationData: type = Union[FlagLocationData, DexLocationData, TMLocationData]
AnyEncounterData: type = Union[EncounterData, TradeEncounterData, StaticEncounterData]
