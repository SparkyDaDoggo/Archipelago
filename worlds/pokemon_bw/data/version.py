from typing import NamedTuple


class VersionCompatibility(NamedTuple):
    patch_file: tuple[int, int, int]
    rom: tuple[int, int, int]
    ut: tuple[int, int, int]


# DO NOT put any number higher than 255
version: tuple[int, int, int] = (0, 4, 0)

compatibility: dict[tuple[int, int, int], VersionCompatibility] = {
    (0, 3, 0): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 0)),
    (0, 3, 1): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 0)),
    (0, 3, 2): VersionCompatibility((0, 3, 0), (0, 3, 2), (0, 3, 2)),
    (0, 3, 3): VersionCompatibility((0, 3, 0), (0, 3, 3), (0, 3, 2)),
    (0, 3, 4): VersionCompatibility((0, 3, 0), (0, 3, 4), (0, 3, 2)),
    (0, 3, 5): VersionCompatibility((0, 3, 0), (0, 3, 4), (0, 3, 2)),
    (0, 3, 6): VersionCompatibility((0, 3, 0), (0, 3, 4), (0, 3, 6)),
    (0, 3, 7): VersionCompatibility((0, 3, 0), (0, 3, 4), (0, 3, 6)),
    (0, 3, 99): VersionCompatibility((0, 3, 99), (0, 3, 99), (0, 3, 6)),
    (0, 3, 999): VersionCompatibility((0, 3, 99), (0, 3, 200), (0, 3, 6)),
    (0, 4, 0): VersionCompatibility((0, 4, 0), (0, 4, 0), (0, 4, 0)),
}


def patch_file() -> tuple[int, int, int]:
    return compatibility[version].patch_file


def rom() -> tuple[int, int, int]:
    return compatibility[version].rom


def ut() -> tuple[int, int, int]:
    return compatibility[version].ut


if __name__ == "__main__":
    import orjson
    import os
    import zipfile

    apworld = "pokemon_bw"

    with zipfile.ZipFile("D:/Games/Archipelago/custom_worlds/dev/"+apworld+".apworld", 'w', zipfile.ZIP_DEFLATED, True, 9) as zipf:
        metadata = {
            "game": "Pokemon Black and White",
            "minimum_ap_version": "0.6.3",
            "authors": ["BlastSlimey", "SparkyDaDoggo"],
            "world_version": ".".join(str(i) for i in version)
        }
        zipf.writestr(os.path.join(apworld, "archipelago.json"), orjson.dumps(metadata))
        for root, dirs, files in os.walk("../"):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           "../../"))
