from dataclasses import dataclass
from typing import Self, TYPE_CHECKING, Iterator, Literal

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


@dataclass
class EncounterEntry:
    species_id: tuple[int, int]
    encounter_region: tuple[str, str, str]
    file_index: tuple[int, int, int]
    write: int
    """b0 level changed
    b1 species changed"""
    min_level: int
    max_level: int
    region: str = ""

    def build_region(self) -> Self:
        season = '' if not self.encounter_region[1] else f" ({self.encounter_region[1]})"
        self.region = f"{self.encounter_region[0]}{season} - {self.encounter_region[2]}"
        return self


@dataclass
class StaticEncounterEntry:
    species_id: tuple[int, int]
    encounter_region: str
    inclusion_rule: InclusionRule | None
    access_rule: ExtendedRule | None


@dataclass
class TradeEncounterEntry:
    species_id: tuple[int, int]
    wanted_dex_number: int
    encounter_region: str


@dataclass
class TrainerPokemonEntry:
    trainer_id: int
    team_number: int
    species: str
    level: int
    write: int
    """b0 is level
    b1 is species"""
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
    to_check: list[SpeciesEntry]
    already_checked: set[SpeciesEntry]

    def __init__(self, initial: list[SpeciesEntry], world: "PokemonBWWorld"):
        self.to_check = list({entry: 0 for entry in initial})  # list->dict->list to get rid of duplicates, no sets because determinism
        self.already_checked = set()
        self.by_id = world.species_entries_by_id

    def __iter__(self) -> Iterator[SpeciesEntry]:
        return self.to_check.__iter__()

    def __len__(self) -> int:
        return len(self.to_check)

    def copy_list(self) -> list[SpeciesEntry]:
        return self.to_check.copy()

    def add(self, species: SpeciesEntry):
        if species in self.to_check:
            return
        if species in self.already_checked:
            return
        self.to_check.append(species)

    def check(self, species: SpeciesEntry, loop=0):
        if species in self.to_check:
            self.to_check.remove(species)
        self.already_checked.add(species)
        # Looping evolutions are possible if enabled in randomization
        if loop >= 10:
            return
        for evolution in species.evolutions:
            if evolution[0] == "Level up with party member":
                self.add(self.by_id[(evolution[1], 0)])
            for evo_data in evolution[2]:
                if evo_data.form == species.form or (evo_data.form == 0 and
                                                     (evo_data.dex_number, species.form) not in self.by_id):
                    self.check(evo_data, loop+1)


@dataclass
class CopyGroup:
    outer: Self | None
    head: EncounterEntry
    species: SpeciesEntry | None
    chances: dict[tuple[str, str, str], int]

    def search(self) -> Self:
        current = self
        while current.outer:
            current = current.outer
        return current


class CopyChecklist:
    by_file: list[tuple[list[CopyGroup | None], ...] | None]

    def __init__(self):
        self.by_file = [None for _ in range(112)]

    def merge(self, e1: EncounterEntry, e2: EncounterEntry, chance1: int, chance2: int):
        self._check_file_list(e1)
        self._check_file_list(e2)
        e1_group, e2_group = self[e1.file_index], self[e2.file_index]
        if not e1_group and not e2_group:
            if e1.encounter_region == e2.encounter_region:
                chances = {e1.encounter_region: chance1 + chance2}
            else:
                chances = {e1.encounter_region: chance1, e2.encounter_region: chance2}
            self[e1.file_index], self[e2.file_index] = (CopyGroup(None, e1, None, chances), ) * 2
        elif e1_group and e2_group:
            e1_group, e2_group = e1_group.search(), e2_group.search()
            for reg, ch in e2_group.chances.items():
                e1_group.chances[reg] = e1_group.chances.get(reg, 0) + ch
            e2_group.outer = e1_group
            del e2_group.chances
        else:
            self._add_to(e2, e1_group, chance2) if e1_group else self._add_to(e1, e2_group, chance1)

    def _add_to(self, new: EncounterEntry, group: CopyGroup, chance: int):
        group = group.search()
        self[new.file_index] = group
        group.chances[new.encounter_region] = group.chances.get(new.encounter_region, 0) + chance

    def _check_file_list(self, entry: EncounterEntry):
        file = entry.file_index[0]
        if self.by_file[file] is None:
            if not entry.encounter_region[1]:
                self.by_file[file] = ([None] * 56, )
            else:
                self.by_file[file] = ([None] * 56, [None] * 56, [None] * 56, [None] * 56)

    def __getitem__(self, item: tuple[int, int, int]) -> CopyGroup | None:
        if self.by_file[item[0]] is None:
            return None
        return self.by_file[item[0]][item[1]][item[2]]

    def __setitem__(self, key: tuple[int, int, int], value: CopyGroup):
        """Only use from inside!"""
        self.by_file[key[0]][key[1]][key[2]] = value
