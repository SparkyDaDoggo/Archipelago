from dataclasses import dataclass


@dataclass
class Zone:
    map_type: int  # 1 byte
    npc_info_cache: int  # 1 byte
    area: int  # 2 bytes
    matrix: int  # 2 bytes
    scripts: int  # 2 bytes
    init_scripts: int  # 2 bytes
    text: int  # 2 bytes
    bgm_spring: int  # 2 bytes
    bgm_summer: int  # 2 bytes
    bgm_autumn: int  # 2 bytes
    bgm_winter: int  # 2 bytes
    encounter: int  # 2 bytes, only bits 0x1FFF
    unknown: int  # (encounter >> 13) & 7
    entities: int  # 2 bytes
    parent_zone: int  # 2 bytes
    location_name: int  # 2 bytes, only bits 0x3FF
    location_name_display: int  # (location_name >> 10) & 0x3F
    weather: int  # env_flags := 2 bytes, env_flags & 0x3F
    actor_matrix: int  # (env_flags >> 6) & 7
    camera: int  # (env_flags >> 9) & 0x7F
    map_transition: int  # other_flags := 2 bytes, only bits 0x1F
    bgm_battle: int  # (other_flags >> 5) & 0x1F
    enable_cycling: int  # (other_flags >> 10) & 1
    enable_running: int  # (other_flags >> 11) & 1
    enable_escape_rope: int  # (other_flags >> 12) & 1
    enable_fly: int  # (other_flags >> 13) & 1
    enable_bgm_cycling: int  # (other_flags >> 14) & 1
    enable_entralink: int  # (other_flags >> 15) & 1
    matrix_cam_boundaries: int  # 2 bytes, signed
    name_icon: int  # 2 bytes, only bits 0x1FFF
    difficulty: int  # (name_icon >> 13) & 7
    fly_x: int  # 4 bytes
    fly_y: int  # 4 bytes
    fly_z: int  # 4 bytes
