from typing import TYPE_CHECKING

from BaseClasses import Item, Location, LocationProgressType as LocProgType, CollectionState
from Fill import fill_restrictive

if TYPE_CHECKING:
    from .. import PokemonBWWorld


def is_excluded(world: "PokemonBWWorld", location: Location) -> bool:
    return location.progress_type == LocProgType.EXCLUDED or location.name in world.options.exclude_locations


def place_badges_locked(world: "PokemonBWWorld", items: list[Item]) -> None:
    from ..data.locations.ingame_items import special
    from ..data.items import badges

    match world.options.shuffle_badges.current_key:
        case "vanilla":
            # Priority locations are ignored here because of no badges being filler
            # Shuffling items and locations not needed since this option is about specific placement
            badge_items: dict[str, Item] = {
                item.name: item
                for item in items
                if item.name in badges.table
            }
            badge_locations: dict[str, Location] = {
                loc.name: loc
                for loc in world.get_locations()
                if loc.name in special.gym_badges
            }
            placements = {
                "Striaton Gym - Badge reward": "Trio Badge",
                "Nacrene Gym - Badge reward": "Basic Badge",
                "Castelia Gym - Badge reward": "Insect Badge",
                "Nimbasa Gym - Badge reward": "Bolt Badge",
                "Driftveil Gym - Badge reward": "Quake Badge",
                "Mistralton Gym - Badge reward": "Jet Badge",
                "Icirrus Gym - Badge reward": "Freeze Badge",
                "Opelucid Gym - Badge reward": "Legend Badge",
            }
            for loc, it in placements.items():
                if is_excluded(world, badge_locations[loc]):
                    continue
                badge_locations[loc].place_locked_item(badge_items[it])
                items.remove(badge_items[it])  # list.remove() safe here because badges only exist once in local pool
        case "shuffle":
            # Priority locations are ignored here because of no badges being filler
            # Shuffle items because of some locations potentially being skipped
            badge_items: list[Item] = [item for item in items if item.name in badges.table]
            for item in badge_items:
                items.remove(item)  # list.remove() safe here because badges only exist once in local pool
            world.random.shuffle(badge_items)
            # Locations not shuffled since items are shuffled
            locations = list(world.get_locations())
            filled_locations = [loc for loc in locations if loc.item]
            badge_locations: list[Location] = [
                loc
                for loc in locations
                if loc.name in special.gym_badges
                if not is_excluded(world, loc)
            ]
            state = CollectionState(world.multiworld)
            state.sweep_for_advancements(filled_locations)  # In case something in the future will be force-placed before badges
            for item in items:
                state.collect(item, True)
            fill_restrictive(world.multiworld, state, badge_locations, badge_items,
                             single_player_placement=True, lock=True, allow_partial=True, name="Badges shuffle")
            items.extend(badge_items)  # Re-add unplaced to item pool
        case "anything":
            pass
        case _:
            raise Exception(f"Bad shuffle_badges option value for player {world.player_name}")


def place_tm_hm_locked(world: "PokemonBWWorld", items: list[Item]) -> None:
    from ..data.locations.ingame_items.special import tm_hm_ncps, gym_tms
    from ..data.locations import all_tm_locations
    from ..data.items import tm_hm, all_tm_hm

    match world.options.shuffle_tm_hm.current_key:
        case "shuffle":
            # Priority locations are ignored here because of no TMs/HMs being filler
            # Get TMs and HMs shuffled
            tm_hm_items: list[Item] = [item for item in items if item.name in all_tm_hm]
            for item in tm_hm_items:
                items.remove(item)  # list.remove() safe here because badges only exist once in local pool
            world.random.shuffle(tm_hm_items)
            # Shuffle locations to prevent always having all HMs in the same few spots
            locations = list(world.get_locations())
            filled_locations = [loc for loc in locations if loc.item]
            tm_hm_locs: list[Location] = [
                loc
                for loc in locations
                if loc.name in all_tm_locations
                if not is_excluded(world, loc)
            ]
            world.random.shuffle(tm_hm_locs)
            state = CollectionState(world.multiworld)
            state.sweep_for_advancements(filled_locations)  # Consider already placed badges, which has been a problem before
            for item in items:
                state.collect(item, True)
            fill_restrictive(world.multiworld, state, tm_hm_locs, tm_hm_items,
                             single_player_placement=True, lock=True, allow_partial=True, name="TM/HM shuffle")
            items.extend(tm_hm_items)  # Re-add unplaced to item pool
            # TODO what to do with HM rules now?
        case "hm_with_badge":
            tm_items = [item for item in items if item.name in tm_hm.tm and "TM70" not in item.name]
            hm_items = [item for item in items if item.name in tm_hm.hm or "TM70" in item.name]
            for item in tm_items:
                items.remove(item)  # list.remove() safe here because badges only exist once in local pool
            for item in hm_items:
                items.remove(item)  # list.remove() safe here because badges only exist once in local pool
            locations = list(world.get_locations())
            filled_locations = [loc for loc in locations if loc.item]
            other_tm_locations: list[Location] = [
                loc
                for loc in locations
                if loc.name in tm_hm_ncps
                if not is_excluded(world, loc)
            ]
            gym_tm_locations: list[Location] = [
                loc
                for loc in locations
                if loc.name in gym_tms
                if not is_excluded(world, loc)
            ]
            gym_locs_copy = gym_tm_locations.copy()
            state = CollectionState(world.multiworld)
            state.sweep_for_advancements(filled_locations)  # Consider already placed badges, which has been a problem before
            for item in items:
                state.collect(item, True)
            fill_restrictive(world.multiworld, state, gym_tm_locations, hm_items,
                             single_player_placement=True, lock=True, allow_partial=True, name="Gym HMs shuffle")
            state.sweep_for_advancements([loc for loc in gym_locs_copy if loc.item])  # Consider now-placed HMs
            tm_items.extend(hm_items)  # fill_restrictive already removed placed HMs
            fill_restrictive(world.multiworld, state, gym_tm_locations + other_tm_locations, tm_items,
                             single_player_placement=True, lock=True, allow_partial=True, name="Non-gym TMs shuffle")
            items.extend(tm_items)
        case "anything":
            pass
        case _:
            raise Exception(f"Bad shuffle_tm_hm option value for player {world.player_name}")
