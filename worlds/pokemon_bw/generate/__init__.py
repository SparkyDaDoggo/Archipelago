from typing import NamedTuple, TYPE_CHECKING

from ..data import InclusionRule, ExtendedRule

if TYPE_CHECKING:
    from ..data import SpeciesData


class SpeciesEntry(NamedTuple):
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
    evolutions: list[tuple[str, int, str]]
    # tuple(level, move name)
    level_up_moves: list[tuple[int, str]]
    # TM number (internal order is TM1-95 HM1-6)
    tm_hm_moves: set[str]


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
    by_name: dict[str, "SpeciesData"]
    by_id: dict[tuple[int, int], str]

    def __init__(self, initial: list[str]):
        from ..data.pokemon.species import by_name, by_id

        self.to_check = list({entry: 0 for entry in initial})
        self.already_checked = set()
        self.by_name = by_name
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
            self.check(evolution[2], loop+1)
