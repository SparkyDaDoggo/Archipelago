from typing import TYPE_CHECKING
import worlds._bizhawk as bizhawk
from ..tracker import should_change

if TYPE_CHECKING:
    from ..bizhawk_client import PokemonBWClient
    from worlds._bizhawk.context import BizHawkClientContext


async def set_map(client: "PokemonBWClient", ctx: "BizHawkClientContext"):

    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.map_id_offset, 2, client.ram_read_write_domain),
        )
    )
    map_id = int.from_bytes(read[0], "little")
    if 107 <= map_id <= 112 or 120 <= map_id <= 135:
        map_id += (client.game_version << 10)

    if map_id != client.current_map:
        client.current_map = map_id
        if should_change(map_id):
            await ctx.send_msgs([{
                "cmd": "Set",
                "key": f"pokemon_bw_map_{ctx.team}_{ctx.slot}",
                "default": 0,
                "want_reply": False,
                "operations": [{
                    "operation": "replace",
                    "value": map_id,
                }],
            }])


async def set_statics_bitmap(client: "PokemonBWClient", ctx: "BizHawkClientContext"):
    # Excludes legendaries and Volcarona since they're already in the goals bitmap

    bitmap = 0
    if client.get_flag(665):  # Darmanitan left
        bitmap |= 1
    if client.get_flag(663):  # Darmanitan middle left
        bitmap |= 2
    if client.get_flag(664):  # Darmanitan middle
        bitmap |= 4
    if client.get_flag(666):  # Darmanitan middle right
        bitmap |= 8
    if client.get_flag(667):  # Darmanitan right
        bitmap |= 16
    if client.get_flag(2748):  # Musharna
        bitmap |= 32
    if client.get_flag(344):  # Zoroark
        bitmap |= 64
    if client.get_flag(768):  # Route 6 Foongus left
        bitmap |= 128
    if client.get_flag(767):  # Route 6 Foongus right
        bitmap |= 256
    if client.get_flag(772):  # Route 10 Foongus left
        bitmap |= 512
    if client.get_flag(771):  # Route 10 Foongus right
        bitmap |= 1024
    if client.get_flag(770):  # Route 10 Amoongus left
        bitmap |= 2048
    if client.get_flag(769):  # Route 10 Amoongus right
        bitmap |= 4096
    if client.get_flag(339):  # Sold Magikarp
        bitmap |= 8192
    if client.get_flag(315):  # Larvesta egg
        bitmap |= 16384
    if (await client.read_var(ctx, 0xC7)) >= 2:  # Zorua
        bitmap |= 32768
    if bitmap != client.goal_bitmap:
        client.statics_bitmap |= bitmap
        await ctx.send_msgs([{
            "cmd": "Set",
            "key": f"pokemon_bw_static_flags_{ctx.team}_{ctx.slot}",
            "default": 0,
            "want_reply": False,
            "operations": [
                {
                    "operation": "default",
                    "value": 0,
                }, {
                    "operation": "or",
                    "value": bitmap,
                }
            ]
        }])


async def set_trades_bitmap(client: "PokemonBWClient", ctx: "BizHawkClientContext"):

    bitmap = 0
    if client.get_flag(0x1D9):  # Cottonee-Petilil
        bitmap |= 1
    if client.get_flag(0x1DA):  # Minchino-Basculin
        bitmap |= 2
    if client.get_flag(0x1DB):  # Boldore-Emolga
        bitmap |= 4
    if client.get_flag(0x1DC):  # Ditto-Rotom
        bitmap |= 8
    if client.get_flag(0x1DD):  # Cinchino-Munchlax
        bitmap |= 16
    if bitmap != client.goal_bitmap:
        client.trades_bitmap |= bitmap
        await ctx.send_msgs([{
            "cmd": "Set",
            "key": f"pokemon_bw_trade_flags_{ctx.team}_{ctx.slot}",
            "default": 0,
            "want_reply": False,
            "operations": [
                {
                    "operation": "default",
                    "value": 0,
                }, {
                    "operation": "or",
                    "value": bitmap,
                }
            ]
        }])


async def set_goal_bitmap(client: "PokemonBWClient", ctx: "BizHawkClientContext"):

    bitmap = 0
    if client.get_flag(0x1D6):  # N
        bitmap |= 1
    if client.get_flag(0x1D3):  # Ghetsis
        bitmap |= 2
    if (await client.read_var(ctx, 0xE4)) >= 2:  # Cynthia
        bitmap |= 4
    if client.get_flag(705):  # Sage Giallo
        bitmap |= 8
    if client.get_flag(0x1B5):  # Sage Gorm
        bitmap |= 16
    if client.get_flag(0x1D5):  # Sage Zinzolin
        bitmap |= 32
    if client.get_flag(809):  # Sage Ryoku
        bitmap |= 64
    if client.get_flag(0x1D7):  # Sage Rood
        bitmap |= 128
    if client.get_flag(0x1D8):  # Sage Bronius
        bitmap |= 256
    if client.get_flag(779):  # Victini
        bitmap |= 512
    if client.get_flag(0x1CE):  # Reshiram/Zekrom
        bitmap |= 1024
    if client.get_flag(801):  # Kyurem
        bitmap |= 2048
    if client.get_flag(810):  # Volcarona
        bitmap |= 4096
    if client.get_flag(649):  # Cobalion
        bitmap |= 8192
    if client.get_flag(650):  # Terrakion
        bitmap |= 16384
    if client.get_flag(651):  # Virizion
        bitmap |= 32768
    if client.get_flag(0x1D4):  # Alder
        bitmap |= 65536
    if client.get_flag(0x191):  # TM/HM scientist
        bitmap |= 131072
    if client.get_flag(0x178):  # Gym leader Brycen
        bitmap |= 262144
    if client.get_flag(841):  # Daycare man
        bitmap |= 524288
    if bitmap != client.goal_bitmap:
        client.goal_bitmap |= bitmap
        await ctx.send_msgs([{
            "cmd": "Set",
            "key": f"pokemon_bw_events_{ctx.team}_{ctx.slot}",
            "default": 0,
            "want_reply": False,
            "operations": [
                {
                    "operation": "default",
                    "value": 0,
                }, {
                    "operation": "or",
                    "value": bitmap,
                }
            ]
        }])


async def set_dex_caught_seen(client: "PokemonBWClient", ctx: "BizHawkClientContext"):

    packages = []
    read = await bizhawk.read(
        ctx.bizhawk_ctx, (
            (client.save_data_address + client.dex_offset, client.dex_bytes_amount, client.ram_read_write_domain),
            *((client.save_data_address + offset, client.dex_bytes_amount, client.ram_read_write_domain)
              for offset in client.dex_seen_offsets),
        )
    )
    if read[0] != client.tracker_caught_cache:
        caught = [i for i in range(1, 650) if read[0][(i-1)//8] & (2 ** ((i-1) % 8)) > 0]
        for eight_flags in range(len(read[0])):
            client.tracker_caught_cache[eight_flags] |= read[0][eight_flags]
        packages.append({
            "cmd": "Set",
            "key": f"pokemon_bw_caught_{ctx.team}_{ctx.slot}",
            "default": [],
            "want_reply": False,
            "operations": [
                {
                    "operation": "default",
                    "value": [],
                }, {
                    "operation": "update",
                    "value": caught,
                }
            ]
        })
    seen = set()
    for form_num in range(4):
        read_num = read[form_num+1]
        cache = client.tracker_seen_caches[form_num]
        if read_num != cache:
            for i in range(1, 650):
                if read_num[(i-1)//8] & (1 << ((i-1) % 8)):
                    seen.add(i)
            for eight_flags in range(len(read_num)):
                cache[eight_flags] |= read_num[eight_flags]
    if seen:
        packages.append({
            "cmd": "Set",
            "key": f"pokemon_bw_seen_{ctx.team}_{ctx.slot}",
            "default": [],
            "want_reply": False,
            "operations": [
                {
                    "operation": "default",
                    "value": [],
                }, {
                    "operation": "update",
                    "value": list(seen),
                }
            ]
        })
    if packages:
        await ctx.send_msgs(packages)

