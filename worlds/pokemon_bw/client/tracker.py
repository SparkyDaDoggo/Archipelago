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