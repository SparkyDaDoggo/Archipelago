from typing import NamedTuple, Self, TYPE_CHECKING

from ..data import InclusionRule, ExtendedRule, SpeciesData, LevelUpMovesetData, TMHMMovesetData
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

    def __contains__(self, item):
        return item in self.search().members

    def merge(self, other: Self):
        this, other = self.search(), other.search()
        new_line = EvoLine()
        new_line.type, new_line.members = self.type, this.members | other.members
        this.members, other.members = new_line, new_line


class SpeciesEntry:
    dex_name: str
    dex_number: int
    form: int
    type_1: str
    type_2: str
    base_hp: int
    base_attack: int
    base_defense: int
    base_sp_attack: int
    base_sp_defense: int
    base_speed: int
    catch_rate: int
    gender_ratio: int
    # starts with 0 for base evolutions
    evolution_stage: int
    # (primary, secondary, hidden)
    abilities: tuple[str, str, str]
    # tuple(method, parameter, evolve into)
    evolutions: list[tuple[str, int, int]]
    # tuple(level, move name)
    level_up_moves: LevelUpMovesetData
    # TM number (internal order is TM1-95 HM1-6)
    tm_hm_moves: TMHMMovesetData
    is_custom_form: bool
    custom_form_file: int
    # bitflag, b0 = evolutions, b1 = plando evo override, b2 = base stats, b3 = catch rate
    write: int = 0
    evo_line: EvoLine | None = None

    def __init__(self, name: str, data: SpeciesData):
        from ..data.pokemon.species import by_name

        self.dex_name = data.dex_name
        self.dex_number = data.dex_number
        self.form = data.form
        self.type_1 = data.type_1
        self.type_2 = data.type_2
        self.base_hp = data.base_hp
        self.base_attack = data.base_attack
        self.base_defense = data.base_defense
        self.base_sp_attack = data.base_sp_attack
        self.base_sp_defense = data.base_sp_defense
        self.base_speed = data.base_speed
        self.catch_rate = data.catch_rate
        self.gender_ratio = data.gender_ratio
        self.evolution_stage = data.evolution_stage
        self.abilities = data.abilities
        self.evolutions = [(evo_tup[0], evo_tup[1], by_name[evo_tup[2]].dex_number) for evo_tup in data.evolutions]
        self.level_up_moves = movesets_level_up.table[name]
        self.tm_hm_moves = movesets_tm_hm.table[name]
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


class SpeciesChecklist:
    to_check: list[str]
    already_checked: set[str]
    by_name: dict[str, SpeciesEntry]
    by_id: dict[tuple[int, int], str]

    def __init__(self, initial: list[str], world: "PokemonBWWorld"):
        from ..data.pokemon.species import by_id

        self.to_check = list({entry: 0 for entry in initial})
        self.already_checked = set()
        self.by_name = world.species_entries
        self.by_id = by_id

    def __iter__(self):
        return self.to_check.__iter__()

    def __len__(self):
        return len(self.to_check)

    def copy_list(self):
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
        # Looping evolutions are not planned to be prevented
        if loop >= 5:
            return
        data = self.by_name[species]
        for evolution in data.evolutions:
            if evolution[0] == "Level up with party member":
                self.add(self.by_id[(evolution[1], 0)])
            self.check(self.by_id[(evolution[2], data.form)], loop+1)
