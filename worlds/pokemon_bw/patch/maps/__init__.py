from dataclasses import dataclass
from typing import Self


@dataclass
class Zone:
    map_type: int  # 1 byte, data[0]
    npc_info_cache: int  # 1 byte, data[1]
    area: int  # 2 bytes, data[2:4]
    matrix: int  # 2 bytes, data[4:6]
    scripts: int  # 2 bytes, data[6:8]
    init_scripts: int  # 2 bytes, data[8:10]
    text: int  # 2 bytes, data[10:12]
    bgm_spring: int  # 2 bytes, data[12:14]
    bgm_summer: int  # 2 bytes, data[14:16]
    bgm_autumn: int  # 2 bytes, data[16:18]
    bgm_winter: int  # 2 bytes, data[18:20]
    encounter: int  # 2 bytes, only bits 0x1FFF, data[20:22]
    unknown: int  # (encounter >> 13) & 7
    entities: int  # 2 bytes, data[22:24]
    parent_zone: int  # 2 bytes, data[24:26]
    location_name: int  # 2 bytes, only bits 0x3FF, data[26:28]
    location_name_display: int  # (location_name >> 10) & 0x3F
    weather: int  # env_flags := 2 bytes, env_flags & 0x3F, data[28:30]
    actor_matrix: int  # (env_flags >> 6) & 7
    camera: int  # (env_flags >> 9) & 0x7F
    map_transition: int  # other_flags := 2 bytes, only bits 0x1F, data[30:32]
    bgm_battle: int  # (other_flags >> 5) & 0x1F
    enable_cycling: int  # (other_flags >> 10) & 1
    enable_running: int  # (other_flags >> 11) & 1
    enable_escape_rope: int  # (other_flags >> 12) & 1
    enable_fly: int  # (other_flags >> 13) & 1
    enable_bgm_cycling: int  # (other_flags >> 14) & 1
    enable_entralink: int  # (other_flags >> 15) & 1
    matrix_cam_boundaries: int  # 2 bytes, signed, data[32:34]
    name_icon: int  # 2 bytes, only bits 0x1FFF, data[34:36]
    difficulty: int  # (name_icon >> 13) & 7
    fly_x: int  # 4 bytes, data[36:40]
    fly_y: int  # 4 bytes, data[40:44]
    fly_z: int  # 4 bytes, data[44:48]

    def to_bytes(self) -> bytes:
        return (
            bytes((self.map_type, self.npc_info_cache)) +
            self.area.to_bytes(2, "little") +
            self.matrix.to_bytes(2, "little") +
            self.scripts.to_bytes(2, "little") +
            self.init_scripts.to_bytes(2, "little") +
            self.text.to_bytes(2, "little") +
            self.bgm_spring.to_bytes(2, "little") +
            self.bgm_summer.to_bytes(2, "little") +
            self.bgm_autumn.to_bytes(2, "little") +
            self.bgm_winter.to_bytes(2, "little") +
            (self.encounter + (self.unknown << 13)).to_bytes(2, "little") +
            self.entities.to_bytes(2, "little") +
            self.parent_zone.to_bytes(2, "little") +
            (self.location_name + (self.location_name_display << 10)).to_bytes(2, "little") +
            (self.weather + (self.actor_matrix << 6) + (self.camera << 9)).to_bytes(2, "little") +
            (self.map_transition + (self.bgm_battle << 5) +
             (self.enable_cycling << 10) + (self.enable_running << 11) +
             (self.enable_escape_rope << 12) + (self.enable_fly << 13) +
             (self.enable_bgm_cycling << 14) + (self.enable_entralink << 15)).to_bytes(2, "little") +
            self.matrix_cam_boundaries.to_bytes(2, "little", signed=True) +
            (self.name_icon + (self.difficulty << 13)).to_bytes(2, "little") +
            self.fly_x.to_bytes(4, "little") +
            self.fly_y.to_bytes(4, "little") +
            self.fly_z.to_bytes(4, "little")
        )

    @classmethod
    def from_bytes(cls, data: bytes | bytearray, entry: int = 0) -> Self:
        entry *= 48
        return cls(
            data[entry],
            data[entry+1],
            int.from_bytes(data[entry+2:entry+4], "little"),
            int.from_bytes(data[entry+4:entry+6], "little"),
            int.from_bytes(data[entry+6:entry+8], "little"),
            int.from_bytes(data[entry+8:entry+10], "little"),
            int.from_bytes(data[entry+10:entry+12], "little"),
            int.from_bytes(data[entry+12:entry+14], "little"),
            int.from_bytes(data[entry+14:entry+16], "little"),
            int.from_bytes(data[entry+16:entry+18], "little"),
            int.from_bytes(data[entry+18:entry+20], "little"),
            (encounter := int.from_bytes(data[entry+20:entry+22], "little")) & 0x1FFF,
            (encounter >> 13) & 7,
            int.from_bytes(data[entry+22:entry+24], "little"),
            int.from_bytes(data[entry+24:entry+26], "little"),
            (location_name := int.from_bytes(data[entry+26:entry+28], "little")) & 0x3FF,
            (location_name >> 10) & 0x3F,
            (env_flags := int.from_bytes(data[entry+28:entry+30], "little")) & 0x3F,
            (env_flags >> 6) & 7,
            (env_flags >> 9) & 0x7F,
            (other_flags := int.from_bytes(data[entry+30:entry+32], "little")) & 0x1F,
            (other_flags >> 5) & 0x1F,
            (other_flags >> 10) & 1,
            (other_flags >> 11) & 1,
            (other_flags >> 12) & 1,
            (other_flags >> 13) & 1,
            (other_flags >> 14) & 1,
            (other_flags >> 15) & 1,
            int.from_bytes(data[entry+32:entry+34], "little", signed=True),
            (name_icon := int.from_bytes(data[entry+34:entry+36], "little")) & 0x1FFF,
            (name_icon >> 13) & 7,
            int.from_bytes(data[entry+36:entry+40], "little"),
            int.from_bytes(data[entry+40:entry+44], "little"),
            int.from_bytes(data[entry+44:entry+48], "little"),
        )


@dataclass
class Area:
    building: int
    textures: int
    animations: int
    frames: int
    environment: int
    lights: int
    outlines: int
    model_colors: int

    @classmethod
    def from_bytes(cls, data: bytes | bytearray, entry: int = 0):
        entry *= 10
        return cls(
            int.from_bytes(data[entry+0:entry+2], "little"),
            int.from_bytes(data[entry+2:entry+4], "little"),
            data[entry+4],
            data[entry+5],
            data[entry+6],
            data[entry+7],
            data[entry+8],
            data[entry+9],
        )

    def to_bytes(self) -> bytes:
        return (
            self.building.to_bytes(2, "little") +
            self.textures.to_bytes(2, "little") +
            bytes((self.animations, self.frames, self.environment, self.lights, self.outlines, self.model_colors))
        )


@dataclass
class Permissions:
    pass


@dataclass
class Buildings:
    pass


@dataclass
class Container:
    signature: bytes
    model: bytes
    permissions: list[Permissions]
    buildings: Buildings

    def to_bytes(self) -> bytes:
        ret = bytearray(
            self.signature + (len(self.permissions) + 2).to_bytes(2, "little") + bytes(4 * (len(self.permissions) + 3))
        )
        ret[4:8] = len(ret).to_bytes(4, "little")
        ret += self.model
        ret[8:12] = len(ret).to_bytes(4, "little")
        for i in range(len(self.permissions)):
            ret += self.permissions[i].to_bytes()
            ret[12+i*4:16+i*4] = len(ret).to_bytes(4, "little")
        ret += self.buildings.to_bytes()
        ret[12+len(self.permissions)*4:16+len(self.permissions)*4] = len(ret).to_bytes(4, "little")
        return bytes(ret)

    @classmethod
    def from_bytes(cls, data: bytes | bytearray):
        count = int.from_bytes(data[2:4], "little")
        offsets = [int.from_bytes(data[4+c*4:8+c+4], "little") for c in range(count)]
        length = int.from_bytes(data[4+count:8+count], "little")
        return cls(
            data[:2],
            data[offsets[0]:offsets[1]],
            [Permissions.from_bytes(data[offsets[i]:offsets[i+1]]) for i in range(count)],
            Buildings.from_bytes(data[offsets[-1]:length]),
        )
