from typing import TYPE_CHECKING
import worlds._bizhawk as bizhawk

if TYPE_CHECKING:
    from ..bizhawk_client import PokemonBWClient
    from worlds._bizhawk.context import BizHawkClientContext


async def check_flag_locations(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> list[int]:

    if not any(client.missing_flag_loc_ids):
        return []

    locations_to_check: list[int] = []
    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.flags_offset, client.flag_bytes_amount, client.ram_read_write_domain),
        )
    )
    flags_buffer = read[0]
    for eight_flags in range(client.flag_bytes_amount):
        if client.flags_cache[eight_flags] != flags_buffer[eight_flags]:
            merge = client.flags_cache[eight_flags] | flags_buffer[eight_flags]
            if client.flags_cache[eight_flags] != merge:
                for bit in range(8):
                    if merge & (1 << bit) != 0:
                        missing_ids = client.missing_flag_loc_ids[eight_flags*8+bit]
                        for loc_id in missing_ids:
                            locations_to_check.append(loc_id)
                        missing_ids.clear()
            client.flags_cache[eight_flags] = merge
    return locations_to_check


async def check_dex_locations(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> list[int]:

    if not (any(client.missing_dex_flag_loc_ids) or any(client.missing_dexcount_loc_ids)):
        return []

    locations_to_check: list[int] = []
    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.dex_offset, client.dex_bytes_amount, client.ram_read_write_domain),
        )
    )
    dex_buffer = read[0]
    for eight_flags in range(client.dex_bytes_amount):
        if client.dex_cache[eight_flags] == dex_buffer[eight_flags]:
            continue
        merge = client.dex_cache[eight_flags] | dex_buffer[eight_flags]
        if client.dex_cache[eight_flags] != merge:
            new = merge - client.dex_cache[eight_flags]
            for bit in range(8):
                if new & (1 << bit):
                    client.dexsanity_count += 1
                    missing_ids = client.missing_dex_flag_loc_ids[eight_flags * 8 + bit + 1]
                    for loc_id in missing_ids:
                        locations_to_check.append(loc_id)
                    missing_ids.clear()
                    missing_ids = client.missing_dexcount_loc_ids[client.dexsanity_count]
                    for loc_id in missing_ids:
                        locations_to_check.append(loc_id)
                    missing_ids.clear()
        client.dex_cache[eight_flags] = merge
    return locations_to_check


async def check_seen_locations(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> list[int]:

    if not (any(client.missing_shiny_loc_ids) or any(client.missing_shinycount_loc_ids)):
        return []

    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.dex_seen_offsets[0], client.dex_bytes_amount, client.ram_read_write_domain),
            (client.save_data_address + client.dex_seen_offsets[1], client.dex_bytes_amount, client.ram_read_write_domain),
            (client.save_data_address + client.dex_seen_offsets[2], client.dex_bytes_amount, client.ram_read_write_domain),
            (client.save_data_address + client.dex_seen_offsets[3], client.dex_bytes_amount, client.ram_read_write_domain),
        )
    )
    seen_male_buffer, seen_female_buffer, shiny_male_buffer, shiny_female_buffer = seen_buffers = read[0], read[1], read[2], read[3]
    cache0, cache1, cache2, cache3 = client.dex_seen_caches
    # Seen flags should never be unchecked

    if all(seen_buffers[i][eight_flags] == client.dex_seen_caches[i][eight_flags]
           for i in range(4) for eight_flags in range(len(seen_buffers[i]))):
        return []

    locations_to_check: list[int] = []
    seen_dex_nums = set()
    shiny_dex_nums = set()
    for eight_flags in range(client.dex_bytes_amount):
        cache0[eight_flags] = seen_male_buffer[eight_flags]
        cache1[eight_flags] = seen_female_buffer[eight_flags]
        cache2[eight_flags] = shiny_male_buffer[eight_flags]
        cache3[eight_flags] = shiny_female_buffer[eight_flags]
        for bit in range(8):
            # seen male
            if cache0[eight_flags] & (1 << bit):
                seen_dex_nums.add(eight_flags * 8 + bit + 1)
            # seen female
            if cache1[eight_flags] & (1 << bit):
                seen_dex_nums.add(eight_flags * 8 + bit + 1)
            # shiny male
            if cache2[eight_flags] & (1 << bit):
                seen_dex_nums.add(eight_flags * 8 + bit + 1)
                shiny_dex_nums.add(eight_flags * 8 + bit + 1)
            # shiny female
            if cache3[eight_flags] & (1 << bit):
                seen_dex_nums.add(eight_flags * 8 + bit + 1)
                shiny_dex_nums.add(eight_flags * 8 + bit + 1)
    for dex_num in seen_dex_nums:
        locations_to_check += client.missing_seen_loc_ids[dex_num]
        client.missing_seen_loc_ids[dex_num].clear()
    for count in range(len(seen_dex_nums)):
        locations_to_check += client.missing_seencount_loc_ids[count]
        client.missing_seencount_loc_ids[count].clear()
    for dex_num in shiny_dex_nums:
        locations_to_check += client.missing_seen_loc_ids[dex_num]
        client.missing_seen_loc_ids[dex_num].clear()
        locations_to_check += client.missing_shiny_loc_ids[dex_num]
        client.missing_shiny_loc_ids[dex_num].clear()
    for count in range(len(shiny_dex_nums)):
        locations_to_check += client.missing_seencount_loc_ids[count]
        client.missing_seencount_loc_ids[count].clear()
        locations_to_check += client.missing_shinycount_loc_ids[count]
        client.missing_shinycount_loc_ids[count].clear()
    return locations_to_check
