
from typing import TYPE_CHECKING
import worlds._bizhawk as bizhawk
from ..data.items import all_main_items, all_key_items, all_berries, badges, seasons, all_items_dict_view, all_medicine, all_tm_hm, medicine

if TYPE_CHECKING:
    from ..bizhawk_client import PokemonBWClient
    from worlds._bizhawk.context import BizHawkClientContext


async def receive_items(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> None:

    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.var_offset + (2 * 0x126), 4, client.ram_read_write_domain),
        )
    )
    received_items_count = int.from_bytes(read[0], "little")

    if received_items_count >= len(ctx.items_received):
        return

    main_items_bag_buffer: bytearray | None = None
    key_items_bag_buffer: bytearray | None = None
    medicine_bag_buffer: bytearray | None = None
    berry_bag_buffer: bytearray | None = None
    tm_hm_bag_buffer: bytearray | None = None

    new_received = received_items_count
    for index in range(received_items_count, len(ctx.items_received)):
        network_item = ctx.items_received[index]
        name = ctx.item_names.lookup_in_game(network_item.item)
        internal_id = all_items_dict_view[name].item_id
        match name:
            case x if x in all_main_items:
                if main_items_bag_buffer is None:
                    read = await bizhawk.read(
                        ctx.bizhawk_ctx, (
                            (client.save_data_address + client.main_items_bag_offset,
                             client.main_items_bag_size * 4,
                             client.ram_read_write_domain),
                        )
                    )
                    main_items_bag_buffer = bytearray(read[0])
                if not await write_to_bag(client, ctx, main_items_bag_buffer, client.main_items_bag_offset,
                                          client.main_items_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to main items bag, no space left. "
                                          f"Please report this and a list of all items "
                                          f"in your main items bag to the developers.")
                    break
            case x if x in all_key_items:
                if key_items_bag_buffer is None:
                    read = await bizhawk.read(
                        ctx.bizhawk_ctx, (
                            (client.save_data_address + client.key_items_bag_offset,
                             client.key_items_bag_size * 4,
                             client.ram_read_write_domain),
                        )
                    )
                    key_items_bag_buffer = bytearray(read[0])
                if not await write_to_bag(client, ctx, key_items_bag_buffer, client.key_items_bag_offset,
                                          client.key_items_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to key items bag, no space left. "
                                          f"Please report this and a list of all items"
                                          f" in your key items bag to the developers.")
                    break
            case x if x in all_berries:
                if berry_bag_buffer is None:
                    read = await bizhawk.read(
                        ctx.bizhawk_ctx, (
                            (client.save_data_address + client.berry_bag_offset,
                             client.berry_bag_size * 4,
                             client.ram_read_write_domain),
                        )
                    )
                    berry_bag_buffer = bytearray(read[0])
                if not await write_to_bag(client, ctx, berry_bag_buffer, client.berry_bag_offset,
                                          client.berry_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to key items bag, no space left. "
                                          f"Please report this and a list of all items "
                                          f"in your main bag to the developers.")
                    break
            case x if x in badges.table:
                read = await bizhawk.read(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.badges_offset, 1, client.ram_read_write_domain),
                    )
                )
                new_state = read[0][0] | (1 << badges.table[name].bit)
                await bizhawk.write(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.badges_offset, [new_state], client.ram_read_write_domain),
                    )
                )
            case x if x in all_medicine:
                if medicine_bag_buffer is None:
                    read = await bizhawk.read(
                        ctx.bizhawk_ctx, (
                            (client.save_data_address + client.medicine_bag_offset,
                             client.medicine_bag_size * 4,
                             client.ram_read_write_domain),
                        )
                    )
                    medicine_bag_buffer = bytearray(read[0])
                if not await write_to_bag(client, ctx, medicine_bag_buffer, client.medicine_bag_offset,
                                          client.medicine_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to medicine bag, no space left. "
                                          f"Please report this and a list of all items "
                                          f"in your medicine bag to the developers.")
                    break
            case x if x in seasons.table:
                flag = seasons.table[name].flag_id
                new_state = client.flags_cache[flag // 8] | (1 << (flag % 8))
                await bizhawk.write(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.flags_offset, [new_state], client.ram_read_write_domain),
                    )
                )
            case x if x in all_tm_hm:
                if tm_hm_bag_buffer is None:
                    read = await bizhawk.read(
                        ctx.bizhawk_ctx, (
                            (client.save_data_address + client.tm_hm_bag_offset,
                             client.tm_hm_bag_size * 4,
                             client.ram_read_write_domain),
                        )
                    )
                    tm_hm_bag_buffer = bytearray(read[0])
                if not await write_to_bag(client, ctx, tm_hm_bag_buffer, client.tm_hm_bag_offset,
                                          client.tm_hm_bag_size, internal_id, False):
                    client.logger.warning(f"Could not add {name} to TM/HM bag, no space left. "
                                          f"Please report this and a list of all items "
                                          f"in your TM/HM bag to the developers.")
                    break
            case _:
                client.logger.warning(f"Bad item name: {name}")
        new_received += 1

    if new_received > received_items_count:
        await bizhawk.write(
            ctx.bizhawk_ctx, (
                (client.save_data_address + client.var_offset + 2*0x126,
                 new_received.to_bytes(4, "little"),
                 client.ram_read_write_domain),
            )
        )


async def reload_key_items(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> None:

    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.var_offset + (2*0x126), 4, client.ram_read_write_domain),
        )
    )
    received_items_count = int.from_bytes(read[0], "little")

    key_items_bag_buffer: bytearray | None = None
    medicine_bag_buffer: bytearray | None = None
    tm_hm_bag_buffer: bytearray | None = None

    for index in range(received_items_count):
        network_item = ctx.items_received[index]
        name = ctx.item_names.lookup_in_game(network_item.item)
        internal_id = all_items_dict_view[name].item_id
        match name:
            case x if x in all_key_items:
                if key_items_bag_buffer is None:
                    read = await bizhawk.read(
                        ctx.bizhawk_ctx, (
                            (client.save_data_address + client.key_items_bag_offset,
                             client.key_items_bag_size * 4,
                             client.ram_read_write_domain),
                        )
                    )
                    key_items_bag_buffer = bytearray(read[0])
                if not await write_to_bag(client, ctx, key_items_bag_buffer, client.key_items_bag_offset,
                                          client.key_items_bag_size, internal_id, True):
                    client.logger.warning(f"Could not add {name} to key items bag, no space left. "
                                          f"Please report this and a list of all items"
                                          f" in your key items bag to the developers.")
                    break
            case x if x in badges.table:
                read = await bizhawk.read(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.badges_offset, 1, client.ram_read_write_domain),
                    )
                )
                new_state = read[0][0] | (1 << badges.table[name].bit)
                await bizhawk.write(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.badges_offset, [new_state], client.ram_read_write_domain),
                    )
                )
            case x if x in medicine.important:
                if medicine_bag_buffer is None:
                    read = await bizhawk.read(
                        ctx.bizhawk_ctx, (
                            (client.save_data_address + client.medicine_bag_offset,
                             client.medicine_bag_size * 4,
                             client.ram_read_write_domain),
                        )
                    )
                    medicine_bag_buffer = bytearray(read[0])
                if not await write_to_bag(client, ctx, medicine_bag_buffer, client.medicine_bag_offset,
                                          client.medicine_bag_size, internal_id, True):
                    client.logger.warning(f"Could not add {name} to medicine bag, no space left. "
                                          f"Please report this and a list of all items "
                                          f"in your medicine bag to the developers.")
                    break
            case x if x in seasons.table:
                flag = seasons.table[name].flag_id
                new_state = client.flags_cache[flag // 8] | (1 << (flag % 8))
                await bizhawk.write(
                    ctx.bizhawk_ctx, (
                        (client.save_data_address+client.flags_offset, [new_state], client.ram_read_write_domain),
                    )
                )
            case x if x in all_tm_hm:
                if tm_hm_bag_buffer is None:
                    read = await bizhawk.read(
                        ctx.bizhawk_ctx, (
                            (client.save_data_address + client.tm_hm_bag_offset,
                             client.tm_hm_bag_size * 4,
                             client.ram_read_write_domain),
                        )
                    )
                    tm_hm_bag_buffer = bytearray(read[0])
                if not await write_to_bag(client, ctx, tm_hm_bag_buffer, client.tm_hm_bag_offset,
                                          client.tm_hm_bag_size, internal_id, True):
                    client.logger.warning(f"Could not add {name} to TM/HM bag, no space left. "
                                          f"Please report this and a list of all items "
                                          f"in your TM/HM bag to the developers.")
                    break
            case _:
                # Other bags are irrelevant for this part
                pass


async def write_to_bag(client: "PokemonBWClient", ctx: "BizHawkClientContext",
                       buffer: bytearray, bag_offset: int, bag_size: int, internal_id: int, only_once: bool) -> bool:

    # go through all slots in bag
    for slot in range(bag_size):
        id_in_slot = int.from_bytes(buffer[slot*4:(slot*4)+2], "little")

        # slot which already has that item or first empty slot found
        if id_in_slot == internal_id or id_in_slot == 0:
            old_amount = int.from_bytes(buffer[(slot*4)+2:(slot*4)+4], "little")
            if only_once and old_amount > 0:
                return True  # Only when key items get reloaded

            internal_id_bytes = internal_id.to_bytes(2, "little")
            new_amount_bytes = min(old_amount + 1, 995).to_bytes(2, "little")
            # write item id and new amount to slot
            await bizhawk.write(
                ctx.bizhawk_ctx, (
                    (client.save_data_address+bag_offset+(slot*4),
                     internal_id_bytes,
                     client.ram_read_write_domain),
                    (client.save_data_address+bag_offset+(slot*4)+2,
                     new_amount_bytes,
                     client.ram_read_write_domain),
                )
            )
            buffer[slot*4] = internal_id_bytes[0]
            buffer[(slot*4)+1] = internal_id_bytes[1]
            buffer[(slot*4)+2] = new_amount_bytes[0]
            buffer[(slot*4)+3] = new_amount_bytes[1]
            return True

    else:
        # went through all slots and none can be written to
        return False
