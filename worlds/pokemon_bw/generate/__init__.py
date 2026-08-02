from dataclasses import dataclass
from typing import NamedTuple, Self, TYPE_CHECKING, Iterator, Literal

from ..data import InclusionRule, ExtendedRule, SpeciesData, LevelUpMovesetData, TMHMMovesetData, MoveData
from ..data.pokemon import movesets_level_up, movesets_tm_hm

if TYPE_CHECKING:
    from .. import PokemonBWWorld


class EvoLine:
    type: str
    members: set[int] | Self  # ONLY LOOKUP

    def search(self) -> Self:
        curr = self
        while isinstance(curr.members, EvoLine):
            curr = curr.members
        return curr

    def __contains__(self, item: int):
        return item in self.search().members

    def merge(self, other: Self):
        this, other = self.search(), other.search()
        new_line = EvoLine()
        new_line.type, new_line.members = self.type, this.members | other.members
        this.members, other.members = new_line, new_line


class SpeciesEntry:
    dex_name: str
    species_name: str
    dex_number: int
    form: int
    types: tuple[str, str]
    base_stats: tuple[int, int, int, int, int, int]
    base_stats_copy: tuple[int, int, int, int, int, int]
    catch_rate: int
    gender_ratio: int
    exp_curve: int
    # starts with 0 for base evolutions
    evolution_stage: int
    # (primary, secondary, hidden)
    abilities: tuple[str, str, str]
    # tuple(method, parameter, evolve into)
    evolutions: list[tuple[str, int, tuple[Self, ...]]]
    evolutions_copy: list[tuple[str, int, int]]  # This is just for comparison
    pre_evolutions: dict[Self, bool]
    # tuple(level, move name)
    level_up_moves: LevelUpMovesetData
    vanilla_moves_count: int
    # TM number (internal order is TM1-95 HM1-6)
    tm_hm_moves: TMHMMovesetData
    egg_groups: tuple[str, str] | None
    egg_species: str | None
    is_custom_form: bool
    custom_form_file: int
    write: int = 0
    """b0 = evolutions
    b1 = plando evo override
    b2 = base stats
    b3 = catch rate
    b4 = levelup moveset
    b5 = types
    b6 = tm/hm compatibility
    b7 = exp curve
    b8 = egg groups
    b9 = egg species"""
    evo_line: EvoLine | None = None  # Only instantiated when randomized

    def __init__(self, name: str, data: SpeciesData):
        self.dex_name = data.dex_name
        self.species_name = data.species_name or data.dex_name
        self.dex_number = data.dex_number
        self.form = data.form
        self.types = data.types
        self.base_stats = data.base_stats
        self.base_stats_copy = data.base_stats
        self.catch_rate = data.catch_rate
        self.gender_ratio = data.gender_ratio
        self.exp_curve = data.exp_curve
        self.evolution_stage = data.evolution_stage
        self.abilities = data.abilities
        self.evolutions = []  # Gets filled from outside of __init__
        self.evolutions_copy = []  # Gets filled from outside of __init__
        self.pre_evolutions = {}  # Gets filled from outside of __init__
        self.level_up_moves = movesets_level_up.table[name]
        self.vanilla_moves_count = len(self.level_up_moves)
        self.tm_hm_moves = movesets_tm_hm.table[name]
        self.egg_groups = None
        self.egg_species = None
        self.is_custom_form = data.is_custom_form
        self.custom_form_file = data.custom_form_file


class EncounterEntry(NamedTuple):
    species_id: tuple[int, int]
    encounter_region: str
    file_index: tuple[int, int, int]
    write: bool


class StaticEncounterEntry(NamedTuple):
    species_id: tuple[int, int]
    encounter_region: str
    inclusion_rule: InclusionRule | None
    access_rule: ExtendedRule | None


class TradeEncounterEntry(NamedTuple):
    species_id: tuple[int, int]
    wanted_dex_number: int
    encounter_region: str


class TrainerPokemonEntry(NamedTuple):
    trainer_id: int
    team_number: int
    species: str
    # ability: int
    # nature: int
    # held_item: str | None
    # moves: tuple[str, str, str, str] | None


class MoveEntry:
    id: int
    type: str
    category: Literal["Physical", "Special", "Status"]
    power: int
    accuracy: int
    pp: int
    name: str
    write: int = 0
    """b0 = general data
    b1 = name"""

    def __init__(self, name: str, data: MoveData):
        self.id = data.id
        self.type = data.type
        self.category = data.category
        self.power = data.power
        self.accuracy = data.accuracy
        self.pp = data.pp
        self.name = name


class SpeciesChecklist:
    to_check: list[str]
    already_checked: set[str]
    by_name: dict[str, SpeciesEntry]
    by_id: dict[tuple[int, int], SpeciesEntry]

    def __init__(self, initial: list[str], world: "PokemonBWWorld"):
        self.to_check = list({entry: 0 for entry in initial})  # list->dict->list to get rid of duplicates, no sets because determinism
        self.already_checked = set()
        self.by_name = world.species_entries
        self.by_id = world.species_entries_by_id

    def __iter__(self) -> Iterator[str]:
        return self.to_check.__iter__()

    def __len__(self) -> int:
        return len(self.to_check)

    def copy_list(self) -> list[str]:
        return self.to_check.copy()

    def add(self, species: str):
        if species in self.to_check:
            return
        if species in self.already_checked:
            return
        self.to_check.append(species)

    def check(self, species: str, loop=0):
        if species in self.to_check:
            self.to_check.remove(species)
        self.already_checked.add(species)
        # Looping evolutions are possible if enabled in randomization
        if loop >= 5:
            return
        data = self.by_name[species]
        for evolution in data.evolutions:
            if evolution[0] == "Level up with party member":
                self.add(self.by_id[(evolution[1], 0)].species_name)
            for evo_data in evolution[2]:
                if evo_data.form == data.form or (evo_data.form == 0 and (evo_data.dex_number, data.form) not in self.by_id):
                    self.check(evo_data.species_name, loop+1)
