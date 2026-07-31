from typing import NamedTuple, Callable, Literal, TYPE_CHECKING, TypeVar, Any, Union

from BaseClasses import ItemClassification, LocationProgressType, CollectionState

if not TYPE_CHECKING:
    AccessRule: type = Any
    ExtendedRule: type = Any
    ClassificationMethod: type = Any
    ProgressTypeMethod: type = Any
    InclusionRule: type = Any
    RulesDict: type = Any
else:
    from .. import PokemonBWWorld
    AccessRule: type = Callable[[CollectionState], bool]
    ExtendedRule: type = Callable[[CollectionState, PokemonBWWorld], bool]
    ClassificationMethod: type = Callable[[PokemonBWWorld, str], ItemClassification]
    ProgressTypeMethod: type = Callable[[PokemonBWWorld], LocationProgressType]
    InclusionRule: type = Callable[[PokemonBWWorld], bool]
    RulesDict: type = dict[ExtendedRule | tuple[ExtendedRule, ...], AccessRule]

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


class FlagLocationData(NamedTuple):
    # flags begin at 0x23bf28 (B) or 0x23bf48 (W)
    flag_id: int
    progress_type: ProgressTypeMethod
    region: str
    inclusion_rule: InclusionRule | None
    rule: ExtendedRule | None


class TMLocationData(NamedTuple):
    flag_id: int
    progress_type: ProgressTypeMethod
    region: str
    inclusion_rule: InclusionRule | None
    hm_rule: Callable[[str], bool] | None
    rule: ExtendedRule | None


class DexLocationData(NamedTuple):
    # caught flags are stored at 0x23D1B4 (B) or 0x23D1D4 (W)
    dex_number: int
    # Use special rule if there are more than one species for a dex entry (e.g. Wormadam, Deoxys, Castform, ...)
    special_rule: ExtendedRule | None = None
    ut_alias: str | None = None


class TrainerLocationData(NamedTuple):
    trainer_ids: int | tuple[int, ...]
    region: str
    # common_script: bool
    inclusion_rule: InclusionRule | None
    rule: ExtendedRule | None


class EncounterData(NamedTuple):
    species_black: tuple[int, int]
    species_white: tuple[int, int]
    encounter_region: str
    file_index: tuple[int, int, int]


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
    gym: tuple[str, str, bool] | None  # (City name (without the "City") or League, vanilla type, is leader)
    rival: int  # 0 no rival, 1 Bianca, 2 Cheren, 3 N
    # early: bool
    # region: str
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
    exiting_region: str
    entering_region: str
    rule: ExtendedRule | None


class EncounterRegionConnectionData(NamedTuple):
    exiting_region: str
    entering_region: str
    rules: tuple[ExtendedRule, ...] | ExtendedRule | None
    inclusion_rule: InclusionRule | None  # None means always included


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
    # Takes value from evolution data and returns the access rule for that evolution
    rule: Callable[[int, str, "PokemonBWWorld"], ExtendedRule] | None


class TypeData(NamedTuple):
    id: int


class EggGroupData(NamedTuple):
    id: int
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
