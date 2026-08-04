from .rules import *
from .. import EventData, ExtendedRule, IfExtRules as IF


def chain_event(preceding: str) -> ExtendedRule:
    return lambda state, world: state.has("[Event] "+preceding, world.player)


table: list[EventData] = [  # TODO add "[Event] " in generation
    EventData("Argument in Bianca's house", "Bianca's House", shuffled_doors, None),
    EventData("Introduction in Juniper's Lab", "Juniper's Lab", shuffled_doors, None),
    EventData("Accumula Town PC tutorial", "Accumula Town Pokémon Center", shuffled_doors, None),
    EventData("Accumula Town Ghetsis speech", "Accumula Town", shuffled_doors, chain_event("Accumula Town PC tutorial")),
    EventData("Trainers' School Cheren fight", "Striaton City Trainers' School", shuffled_doors, None),
    EventData("Defeating Leader Cilan/Chili/Cress", "Striaton Gym", None, None),
    EventData("Meeting Fennel in Striaton City", "Striaton City Near Gym", shuffled_doors, chain_event("Defeating Leader Cilan/Chili/Cress")),
    EventData("First talk with Fennel in her house", "Striaton City East Upper House 2F", shuffled_doors, chain_event("Meeting Fennel in Striaton City")),
    EventData("Dreamyard North Plasma fight", "Dreamyard North West", None, IF(shuffled_doors, chain_event("First talk with Fennel in her house"))),
    EventData("Grunts running on Route 3", "Route 3 North", shuffled_doors, None),
    EventData("Wellspring Cave Plasma fight", "Wellspring Cave Entrance", shuffled_doors, chain_event("Grunts running on Route 3")),
    # TODO Nacrene stuff at beginning and after Relic Castle
    EventData("Defeating leader Lenora", "Nacrene Gym", None, None),
    EventData("Moss Rock", "Pinwheel Forest South", None, None),
    EventData("Moss Rock", "Pinwheel Forest North", shuffled_doors, None),
    EventData("Moss Rock", "Pinwheel Forest North East", shuffled_doors, None),
    EventData("Burgh running out of gym", "Castelia City Gym Street", shuffled_doors, None),
    EventData("Meetup at Prime Pier", "Castelia City Prime Pier", shuffled_doors, chain_event("Burgh running out of gym")),
    EventData("Burgh searching outside gym street", "Castelia City", shuffled_doors, chain_event("Meetup at Prime Pier")),
    EventData("Burgh searching outside gym street", "Castelia City Central Plaza", shuffled_doors, chain_event("Meetup at Prime Pier")),
    EventData("Castelia Plasma fight", "Castelia City Gym Street", shuffled_doors, chain_event("Burgh searching outside gym street")),
    EventData("Castelia Plasma Hideout confrontation", "Castelia City Plasma Hideout 1F", shuffled_doors, chain_event("Castelia Plasma Fight")),
    EventData("Defeating Leader Burgh", "Castelia Gym", None, None),
    EventData("Defeating Catelia Dancer Mickey", "Castelia City Central Plaza", shuffled_doors, None),
    EventData("Defeating Catelia Dancer Raymond", "Castelia City Unity Pier", shuffled_doors, chain_event("Defeating Catelia Dancer Mickey")),
    EventData("Defeating Catelia Dancer Edmond", "Castelia City Narrow Street", shuffled_doors, chain_event("Defeating Catelia Dancer Mickey")),
    # TODO desert resort/relic castle stuff
    # TODO nimbasa city stuff
    EventData("Helping old man in Nimbasa", "Nimbasa City", None, None),
    # Everything after Nimbasa City is not dependant on door shuffle anymore, as the early spheres whould be over at this point
    # TODO driftveil city stuff
    # TODO chargestone cave stuff
    EventData("Magnetic Area", "Chargestone Cave 1F", None, None),
    EventData("Magnetic Area", "Chargestone Cave B1F", shuffled_doors, None),
    EventData("Magnetic Area", "Chargestone Cave B2F", shuffled_doors, None),
    # TODO mistralton city stuff
    EventData("Ring bell Celestial Tower", "Celestial Tower 5F", None, None),
    EventData("Defeat leader Skyla", "Mistralton Gym", None, None),
    EventData("Talked with kids Mistralton", "Mistralton City North House", None, chain_event("Defeat leader Skyla")),
    # TODO victory road all outside regions can fly to 1F center, add an event for each region and one connection from Menu to VC o 1F Center
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
    EventData("AAAAAA", "AAAAAA", None, None),
]
