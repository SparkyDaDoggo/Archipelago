from typing import TYPE_CHECKING
import worlds._bizhawk as bizhawk

if TYPE_CHECKING:
    from ..bizhawk_client import PokemonBWClient
    from worlds._bizhawk.context import BizHawkClientContext


async def early_setup(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> None:
    from .goals import get_method

    client.goal_checking_method = get_method(client, ctx)

    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.data_address_address, 3, client.ram_read_write_domain),
        )
    )
    client.save_data_address = int.from_bytes(read[0], "little")


async def late_setup(client: "PokemonBWClient", ctx: "BizHawkClientContext") -> None:
    from ..data.version import version
    from .items import reload_key_items

    await reload_key_items(client, ctx)
    opt = ctx.slot_data["options"]

    # Things that should only be done once at the start of the game
    if not client.get_flag(0x1DE):

        # all pokemon seen: male seen, female seen, male shown, forms seen, forms shown
        # shown flags always the later ones, so setting them to male won't change it if a different form was set ingame
        # this will be kept here in client setup instead of scripting system, because the dex flag set command cannot
        #   differentiate gender, which will be important for Gendersanity
        if opt["all_pokemon_seen"]:
            seen_flags = bytearray(b'\xff') * 0x54
            for dex in set(ctx.slot_data["disallowed_all_seen"]):  # iterating over set allowed here since this is not generation
                seen_flags[dex // 8] -= 1 << (dex % 8)
            await bizhawk.write(
                ctx.bizhawk_ctx, (
                    (client.save_data_address + client.dex_seen_offsets[0], seen_flags, "Main RAM"),
                    (client.save_data_address + client.dex_seen_offsets[1], seen_flags, "Main RAM"),
                    (client.save_data_address + client.dex_display_offsets[0], seen_flags, "Main RAM"),
                    (client.save_data_address + client.dex_display_offsets[1], seen_flags, "Main RAM"),
                    (client.save_data_address + client.dex_forms_offsets[0], b'\xff' * 9, "Main RAM"),
                    (client.save_data_address + client.dex_forms_offsets[2], b'\xff' * 9, "Main RAM"),
                )
            )

        # Late setup flag
        await client.write_set_flag(ctx, 0x1DE)

    # Things that also should only be done once, but also after an update
    # If things are added here, it's most likely temporary and will be moved to the upper section later
    version_int = version[2] + (version[1] << 8) + (version[0] << 16)
    if version_int != (await client.read_var(ctx, 0x128, 3)):

        # Versioned late setup var
        await client.write_var(ctx, 0x128, version_int, 3)
