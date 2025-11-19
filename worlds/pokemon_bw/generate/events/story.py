from typing import TYPE_CHECKING, Callable

from ...locations import PokemonBWLocation
from BaseClasses import ItemClassification, CollectionState
from ...items import PokemonBWItem

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def create(world: "PokemonBWWorld") -> None:

    events: list[tuple[str, str, Callable[[CollectionState], bool] | None]] = [
        ("Striaton City", "[Event] Striaton Gym", None),
        ("Dreamyard North", "[Event] Team Plasma Dreamyard", None),
        ("Dreamyard South", "[Event] Find sage Gorm", None),
        ("Nacrene City", "[Event] Nacrene Gym", None),
        ("Pinwheel Forest West", "[Event] Team Plasma Pinwheel Forest", None),
        ("Castelia City", "[Event] Team Plasma Castelia City", None),
        ("Castelia City", "[Event] Castelia Gym",
         lambda state: state.has("[Event] Team Plasma Castelia City", world.player)),
        ("Relic Castle Lower Floors", "[Event] Team Plasma Relic Castle", None),
        ("Relic Castle Basement", "[Event] Find sage Ryoku", None),
        ("Nimbasa City", "[Event] Team Plasma Nimbasa City", None),
        ("Nimbasa City", "[Event] Nimbasa Gym", None),
        ("Driftveil City", "[Event] Driftveil Gym",
         lambda state: state.has("[Event] Team Plasma Cold Storage", world.player)),
        ("Cold Storage", "[Event] Team Plasma Cold Storage", None),
        ("Cold Storage", "[Event] Find sage Zinzolin", None),
        ("Mistralton Cave Inner", "[Event] Encounter Cobalion", None),
        ("Chargestone Cave", "[Event] Team Plasma Chargestone Cave", None),
        ("Chargestone Cave", "[Event] Find sage Bronius", None),
        ("Mistralton City", "[Event] Mistralton Gym",
         lambda state: state.has("[Event] Skyla Celestial Tower", world.player)),
        ("Celestial Tower", "[Event] Skyla Celestial Tower", None),
        ("Icirrus City", "[Event] Icirrus Gym", None),
        ("Dragonspiral Tower", "[Event] Team Plasma Dragonspiral Tower", None),
        ("Route 8", "[Event] Bianca Route 8", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
        ("AAAAAAAAAAAAA", "[Event] AAAAAAAAAAAAA", None),
    ]

    for region, name, rule in events:
        loc = PokemonBWLocation(world.player, name, None, world.regions[region])
        world.regions[region].locations.append(loc)
        loc.place_locked_item(
            PokemonBWItem(name, ItemClassification.progression, None, world.player)
        )
        if rule is not None:
            loc.access_rule = rule
