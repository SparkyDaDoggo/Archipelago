import logging
import typing
from copy import deepcopy

import settings
from BaseClasses import PlandoOptions
from Options import OptionError, Option
from ..data.common_options import ToggleSet, ExtendedOptionCounter

if typing.TYPE_CHECKING:
    from worlds.AutoWorld import World


class RandomizeMoveData(ToggleSet):
    """
    Randomizes various move data.
    You can add as many of the following modifiers as you want.

    - **Shuffle power** - Gives every damaging move a commonly used power value
        (e.g. 50, 75, 100, ...) in an adjustable range. Moves with a unique damage
        calculation are not affected.
    - **Randomize power** - Gives every move a completely random power value in an
        adjustable range. Supersedes **Shuffle power**. Moves with a unique damage
        calculation are not affected.
    - **Randomize type** - Randomizes the type of each move, with the Normal type
        having an adjustable chance.
    - **Shuffle accuracy** - Gives every move a commonly used accuracy
        (e.g. 100, 95, 50, ...) in an adjustable range. Moves with a guaranteed hit
        chance are not affected.
    - **Randomize accuracy** - Gives every move a completely random accuracy in an
        adjustable range. Supersedes **Shuffle accuracy**. Moves with a guaranteed hit
        chance are not affected.
    - **Randomize category** - Randomizes the category of all physical and special moves.
        Status moves are not affected.
    - **Shuffle PP** - Gives every move a commonly used maximum PP count
        (e.g. 10, 15, 25, ...) in an adjustable range.
    - **Randomize PP** - Gives every move a completely random maximum PP count in an
        adjustable range. Supersedes **Shuffle PP**.

    - **Correlate power and PP** - Moves with a higher PP count are more likely to be
        less powerful, if any of the two are randomized.
    - **Correlate power and accuracy** - Moves with a lower accuracy are more likely to
        be more powerful, if any of the two are randomized.
    - **Correlate PP and accuracy** - Moves with a lower PP count are more likely to
        have a higher accuracy, if any of the two are randomized.
    """
    _: None
    """
    - **Shuffle name** - Shuffles all move names between each other.
    - **Randomize name** - Gives every move a random name made of 1-2 words from a pool
        of ~1000 english words.
        
    - **Allow other languages** - Allows names to be made of words from other languages
        than english, if randomized (not just shuffled).
    - **Allow mixed languages** - Allows 2-word-names to be made of words from different
        languages instead of just english, if randomized (not just shuffled).
        Supersedes **Allow other languages**.

    - **Correlate name and type** - Names will be made of words that fit the type of
        the move (or are overall neutral), if names are randomized (not just shuffled).
    """
    display_name = "Randomize Move Power"
    is_shuffle_power = False
    is_randomize_power = False
    is_randomize_type = False
    is_shuffle_accuracy = False
    is_randomize_accuracy = False
    is_randomize_category = False
    is_shuffle_pp = False, "Shuffle PP"
    is_randomize_pp = False, "Randomize PP"
    # is_shuffle_name = False
    # is_randomize_name = False
    # is_allow_other_languages = False
    # is_allow_mixed_languages = False
    is_correlate_power_and_pp = False, "Correlate power and PP"
    is_correlate_power_and_accuracy = False
    is_correlate_pp_and_accuracy = False, "Correlate PP and accuracy"
    # is_correlate_name_and_type = False


class RandomizeTypeChart(ToggleSet):
    """
    Randomizes the type effectiveness chart.
    You can add as many of the following modifiers as you want.

    - **Shuffle** - Shuffles all type effectiveness, thereby keeping the overall amount
        of weaknesses, resistances, and immunities. Automatically added if any other
        modifier is added.
    - **Randomize** - Completely randomizes all type effectiveness. Supersedes **Shuffle**.
    - **Disable weaknesses/resistances/immunities** - Prevents all type matchups from
        being a weakness/resistance/immunity (respectively).
    """
    display_name = "Randomize Type Chart"
    is_shuffle = False
    is_randomize = False
    is_disable_weaknesses = False
    is_disable_resistances = False
    is_disable_immunities = False
    auto_add_if_any = "Shuffle"


class MoveDataRandomizationAdjustments(ExtendedOptionCounter):
    """
    Adjust various parameters in various randomization options.
    Any minimum parameter cannot be higher than its corresponding maximum parameter.
    Every parameter can be specified as unweighted/weighted lists, "random",
    and "random-range-x-y" like usual range options.

    - **Move power minimum/maximum** (5-250) - The minimum/maximum move power, if randomized.
    - **Accuracy minimum/maximum** (5-100) - The minimum/maximum accuracy, if randomized.
    - **PP minimum/maximum** (1-250) - The minimum/maximum PP, if randomized.
    - **Normal type probability** (10-90) - The chance of a move becoming a normal type,
        if randomized.
    """
    display_name = "Move Data Randomization Adjustments"
    fill_defaults = True
    valid_keys = [
        "Move power minimum",
        "Move power maximum",
        "Accuracy minimum",
        "Accuracy maximum",
        "PP minimum",
        "PP maximum",
        "Normal type probability",
    ]
    default = {
        "Move power minimum": 5,
        "Move power maximum": 150,
        "Accuracy minimum": 50,
        "Accuracy maximum": 100,
        "PP minimum": 5,
        "PP maximum": 40,
        "Normal type probability": 30,
    }
    individual_min_max = {
        "Move power minimum": (5, 250),
        "Move power maximum": (5, 250),
        "Accuracy minimum": (5, 100),
        "Accuracy maximum": (5, 100),
        "PP minimum": (1, 250),
        "PP maximum": (1, 250),
        "Normal type probability": (10, 90),
    }
    min_max_pairs = [
        ("Move power minimum", "Move power maximum"),
        ("Accuracy minimum", "Accuracy maximum"),
        ("PP minimum", "PP maximum"),
    ]


def plando_to_slotdata(value) -> typing.Any:
    if isinstance(value, dict):
        return {v: plando_to_slotdata(vv) for v, vv in value.items()}
    if isinstance(value, tuple) and hasattr(value, "_fields") and hasattr(value, "_asdict"):
        return {v: plando_to_slotdata(vv) for v, vv in value._asdict().items()}
    if not isinstance(value, str) and isinstance(value, typing.Iterable):
        return tuple(plando_to_slotdata(v) for v in value)
    return value


class PlandoMoveData(typing.NamedTuple):
    power: int = 0
    type: str = ""
    accuracy: int = 0
    category: str = ""
    pp: int = 0
    # name: str = ""


class PlandoTypeEffect(typing.NamedTuple):
    effectiveness: int


class PlandoTMContent(typing.NamedTuple):
    move: str


class MoveDataPlando(Option[dict[str, PlandoMoveData | PlandoTypeEffect | PlandoTMContent]]):
    """
    Here you can change the data of moves and type effectiveness to your liking,
    regardless of whether they're randomized or not.

    Here's an example of how this would look like:
    ```
    move_data_plando:
      Tackle:
        power: 120
        type: Dragon
        accuracy: 30
        category: Special
        pp: 250
      ThunderShock:
        power: 5
        pp: 1
      Normal_Ice:
        effectiveness: 4
      Psychic_Bug:
        effectiveness: 0
    ```

    Move Data Plando requires the corresponding host setting to be enabled, else it will
    be ignored for all players. Be aware that this can lead to generation failures or
    potential softlocks when combined with other restrictive options.
    Refer to the Move Data Plando guide of this game for further information.
    """
    _ = None
    """
    Here you can change the data of moves, type effectiveness, and the content of TMs/HMs
    to your liking, regardless of whether they're randomized or not.
    
      TM95:
        move: Tackle
    """
    display_name = "Move Data Plando"
    supports_weighting = False
    default = {}

    def __init__(self, value: dict[str, PlandoMoveData | PlandoTypeEffect | PlandoTMContent]) -> None:
        self.value = deepcopy(value)
        super().__init__()

    @classmethod
    def from_any(cls, data: dict) -> typing.Self:
        from ..data.pokemon.moves import by_name as moves_by_name
        from ..data.pokemon.types import by_name as types_by_name

        if not isinstance(data, dict):
            raise OptionError(f"Expected dictionary for Move Data Plando, got {type(data)}")
        plandos: dict[str, PlandoMoveData | PlandoTypeEffect | PlandoTMContent] = {}
        for key, plando in data.items():
            if not isinstance(key, str):
                raise OptionError(f"Move Data Plando key expected to be a string, got {type(plando)}")
            if isinstance(plando, PlandoMoveData | PlandoTypeEffect | PlandoTMContent):
                plandos[key] = plando
                continue
            if not isinstance(plando, dict):
                raise OptionError(f"Expected dictionary as Move Data Plando entry for key {key}, got {type(plando)}")
            if key in moves_by_name:
                for plando_key, value in plando.items():
                    if plando_key not in PlandoMoveData._fields:
                        raise OptionError(f"Unknown move data entry key: {plando_key}")
                plandos[key] = PlandoMoveData(**plando)
            else:
                key_split = key.split("_")
                if len(key_split) == 2 and key_split[0] in types_by_name and key_split[1] in types_by_name:
                    for plando_key, value in plando.items():
                        if plando_key not in PlandoTypeEffect._fields:
                            raise OptionError(f"Unknown type effectiveness entry key: {plando_key}")
                    for field in PlandoTypeEffect._fields:
                        if field not in PlandoTypeEffect._field_defaults and field not in plando:
                            raise OptionError(f"Type effectiveness entry {key} is missing the '{field}' key")
                    plandos[key] = PlandoTypeEffect(**plando)
                else:
                    raise OptionError(f"{key} is neither a move name, nor a type effectiveness key")
        return cls(plandos)

    def verify(self, world: typing.Type["World"], player_name: str, plando_options: "PlandoOptions") -> None:
        if not settings.get_settings()["pokemon_bw_settings"]["enable_move_data_plando"]:
            self.value = []
            logging.warning(
                f"The move data plando setting is turned off, so plandos for {player_name} will be ignored."
            )
            return
        try:
            self.verify_keys()
        except OptionError as validation_error:
            raise OptionError(f"Player {player_name} has invalid option keys:\n{validation_error}")

    def verify_keys(self) -> None:
        from ..data.pokemon.moves import by_name as moves_by_name
        from ..data.pokemon.types import by_name as types_by_name

        invalid: list[str] = []
        for plando in self:
            reasons = []
            if isinstance(plando[1], PlandoMoveData):
                if plando[1].power not in range(5, 251) and plando[1].power != 0:
                    reasons.append(f"Move power is not an integer in range 5-250: {plando[1].power}")
                if plando[1].accuracy not in range(5, 100) and plando[1].accuracy != 0:
                    reasons.append(f"Move accuracy is not an integer in range 5-100: {plando[1].accuracy}")
                if plando[1].pp not in range(251):
                    reasons.append(f"Move PP is not an integer in range 1-250: {plando[1].pp}")
                if plando[1].category not in ("Physical", "Special", ""):
                    reasons.append(f"Move category is neither Physical nor Special: {plando[1].category}")
                if plando[1].type not in types_by_name and plando[1].type != "":
                    reasons.append(f"Move type is not a known type: {plando[1].type}")
                if plando[1].power and moves_by_name[plando[0]].power in (0, 1):
                    reasons.append(f"Changing the power of a status move or a move with a unique calculation "
                                   f"({plando[0]}) is not allowed")
                if plando[1].accuracy and moves_by_name[plando[0]].accuracy == 101:
                    reasons.append(f"Changing the accuracy of a move with guaranteed hit chance ({plando[0]}) "
                                   f"is not allowed")
                if plando[1].category and moves_by_name[plando[0]].category == "Status":
                    reasons.append(f"Changing the category of a status move ({plando[0]}) is not allowed")
            else:
                if plando[1].effectiveness not in (0, 2, 4, 8):
                    reasons.append(f"Type effectiveness is not one of the integers 0, 2, 4, or 8: {plando[1].effectiveness}")
            if reasons:
                invalid.append(f"{plando[0]}: " + ", ".join(reasons))
        if invalid:
            raise OptionError(
                f"Invalid Move Data Plando placement(s):\n" +
                "\n".join(invalid) +
                "\nRefer to the Move Data Plando guide of this game for further information."
            )

    def to_slot_data(self) -> list[dict[str, str | list[str] | list[int]]]:
        return plando_to_slotdata(self.value)

    @classmethod
    def get_option_name(cls, value: dict) -> str:
        return str(plando_to_slotdata(value))

    def __iter__(self) -> typing.Iterator[tuple[str, PlandoMoveData | PlandoTypeEffect | PlandoTMContent]]:
        yield from self.value.items()

    def __getitem__(self, index) -> PlandoMoveData | PlandoTypeEffect | PlandoTMContent:
        return self.value[index]

    def __len__(self) -> int:
        return len(self.value)

    def __contains__(self, item) -> bool:
        return item in self.value
