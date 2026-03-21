from typing import TYPE_CHECKING

from BaseClasses import Item, Location, LocationProgressType as LocProgType

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
                items.remove(badge_items[it])  # list.remove() save here because badges only exist once in local pool
        case "shuffle":
            # Priority locations are ignored here because of no badges being filler
            # Shuffle items because of some locations potentially being skipped
            badge_items: list[Item] = [item for item in items if item.name in badges.table]
            world.random.shuffle(badge_items)
            # Locations not shuffled since items are shuffled
            badge_locations: list[Location] = [
                loc
                for loc in world.get_locations()
                if loc.name in special.gym_badges
                if not is_excluded(world, loc)
            ]
            for location in badge_locations:
                item = badge_items.pop()
                location.place_locked_item(item)
                items.remove(item)  # list.remove() save here because badges only exist once in local pool
        case "any_badge":
            pass
        case "anything":
            pass
        case _:
            raise Exception(f"Bad shuffle_badges option value for player {world.player_name}")


def place_badges_fill(world: "PokemonBWWorld",
                      progitempool: list[Item],
                      usefulitempool: list[Item],
                      filleritempool: list[Item],
                      fill_locations: list[Location]) -> None:
    match world.options.shuffle_badges.current_key:
        case "vanilla":
            pass
        case "shuffle":
            pass
        case "any_badge":
            from Fill import fill_restrictive
            from ..data.locations.ingame_items import special

            badge_items: list[Item] = []
            badge_item_indices: list[tuple[int, list[Item]]] = []
            for pool in (progitempool, usefulitempool, filleritempool):
                for index, item in enumerate(pool):
                    if (
                        "badge" in pool[index].name.lower()
                        and (item.player == world.player or
                             item.name not in world.multiworld.worlds[item.player].options.local_items)
                    ):
                        badge_items.append(item)
                        badge_item_indices.append((index, pool))
            for index, pool in reversed(badge_item_indices):  # reversed because else the pop index shifts
                pool.pop(index)
            world.random.shuffle(badge_items)
            badge_locs: list[Location] = [
                loc
                for loc in fill_locations
                if loc.player == world.player and loc.name in special.gym_badges
            ]
            for b_loc in badge_locs:
                fill_locations.remove(b_loc)

            fill_restrictive(world.multiworld, world.multiworld.get_all_state(allow_partial_entrances=True),
                             badge_locs, badge_items, lock=True, allow_partial=True,
                             name=f"PokemonBW_{world.player_name}_any_badge")

            for badge_item in badge_items:
                if badge_item.advancement:
                    progitempool.append(badge_item)
                elif badge_item.useful:
                    usefulitempool.append(badge_item)
                else:
                    filleritempool.append(badge_item)

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
            world.random.shuffle(tm_hm_items)
            # Shuffle locations to prevent always having all HMs in the same few spots
            tm_hm_locs: list[Location] = [
                loc
                for loc in world.get_locations()
                if loc.name in all_tm_locations
                if not is_excluded(world, loc)
            ]
            world.random.shuffle(tm_hm_locs)
            # Take only a slice of items and sort included HMs to front to prevent problems with HM rules
            tm_hm_items = tm_hm_items[:len(tm_hm_locs)]
            to_place = 0
            for to_check in range(1, len(tm_hm_items)):
                if tm_hm_items[to_check].name in tm_hm.hm:
                    tm_hm_items[to_check], tm_hm_items[to_place] = tm_hm_items[to_place], tm_hm_items[to_check]
                    to_place += 1
            for item in tm_hm_items:
                for location in tm_hm_locs:
                    hm_rule = all_tm_locations[location.name].hm_rule
                    if hm_rule is None or hm_rule(item.name):
                        tm_hm_locs.remove(location)
                        location.place_locked_item(item)
                        items.remove(item)  # list.remove() save here because tms/hms only exist once in local pool
                        break
        case "hm_with_badge":
            tm_items = [item for item in items if item.name in tm_hm.tm and "TM70" not in item.name]
            hm_items = [item for item in items if item.name in tm_hm.hm or "TM70" in item.name]
            other_tm_locations: list[Location] = [
                loc
                for loc in world.get_locations()
                if loc.name in tm_hm_ncps
                if not is_excluded(world, loc)
            ]
            gym_tm_locations: list[Location] = [
                loc
                for loc in world.get_locations()
                if loc.name in gym_tms
                if not is_excluded(world, loc)
            ]
            # Shuffle everything
            # If no gym location is excluded, add one random TM to HMs
            if len(gym_tm_locations) == 8:
                rand_tm = world.random.choice(tm_items)
                hm_items.append(rand_tm)
                tm_items.remove(rand_tm)  # list.remove() save here because tms/hms only exist once in local pool
            world.random.shuffle(hm_items)
            world.random.shuffle(other_tm_locations)
            world.random.shuffle(gym_tm_locations)
            # Place HMs into gym locations first
            for loc in gym_tm_locations:
                item = hm_items.pop()
                loc.place_locked_item(item)
                items.remove(item)  # list.remove() save here because tms/hms only exist once in local pool
            # If more than one gym location was excluded, add remaining HMs to TM list and shuffle that
            tm_items.extend(hm_items)
            world.random.shuffle(tm_items)
            # Take only a slice of items and sort included HMs to front to prevent problems with HM rules
            tm_items = tm_items[:len(other_tm_locations)]
            to_place = 0
            for to_check in range(1, len(tm_items)):
                if tm_items[to_check].name in tm_hm.hm:
                    tm_items[to_check], tm_items[to_place] = tm_items[to_place], tm_items[to_check]
                    to_place += 1
            for item in tm_items:
                for location in other_tm_locations:
                    hm_rule = all_tm_locations[location.name].hm_rule
                    if hm_rule is None or hm_rule(item.name):
                        other_tm_locations.remove(location)
                        location.place_locked_item(item)
                        items.remove(item)  # list.remove() save here because tms/hms only exist once in local pool
                        break
        case "any_tm_hm":
            pass
        case "anything":
            pass
        case _:
            raise Exception(f"Bad shuffle_tm_hm option value for player {world.player_name}")


def place_tm_hm_fill(world: "PokemonBWWorld",
                     progitempool: list[Item],
                     usefulitempool: list[Item],
                     filleritempool: list[Item],
                     fill_locations: list[Location]) -> None:
    from ..data.locations import all_tm_locations

    match world.options.shuffle_tm_hm.current_key:
        case "shuffle":
            pass
        case "hm_with_badge":
            pass
        case "any_tm_hm":
            from Fill import fill_restrictive

            tm_hm_items: list[Item] = []
            tm_hm_item_indices: list[tuple[int, list[Item]]] = []
            for pool in (progitempool, usefulitempool, filleritempool):
                for index, item in enumerate(pool):
                    if (
                        len(item.name) > 2 and item.name[:2].lower() in ("tm", "hm") and item.name[2].isdigit()
                        and (item.player == world.player or
                             item.name not in world.multiworld.worlds[item.player].options.local_items)
                    ):
                        tm_hm_items.append(item)
                        tm_hm_item_indices.append((index, pool))
            for index, pool in reversed(tm_hm_item_indices):  # reversed because else the pop index shifts
                pool.pop(index)
            world.random.shuffle(tm_hm_items)
            tm_hm_locs: list[Location] = [
                loc
                for loc in fill_locations
                if loc.player == world.player and loc.name in all_tm_locations
            ]
            for b_loc in tm_hm_locs:
                fill_locations.remove(b_loc)

            fill_restrictive(world.multiworld, world.multiworld.get_all_state(allow_partial_entrances=True),
                             tm_hm_locs, tm_hm_items, lock=True, allow_partial=True,
                             name=f"PokemonBW_{world.player_name}_any_badge")

            for tm_hm_item in tm_hm_items:
                if tm_hm_item.advancement:
                    progitempool.append(tm_hm_item)
                elif tm_hm_item.useful:
                    usefulitempool.append(tm_hm_item)
                else:
                    filleritempool.append(tm_hm_item)

        case "anything":
            pass
        case _:
            raise Exception(f"Bad shuffle_tm_hm option value for player {world.player_name}")
