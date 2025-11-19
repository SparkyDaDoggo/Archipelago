
from typing import NamedTuple


class VersionCompatibility(NamedTuple):
    patch_file: tuple[int, int, int]
    patch_accept: tuple[int, int, int]
    rom: tuple[int, int, int]
    ut: tuple[int, int, int]
    ap_minimum: tuple[int, int, int]


# DO NOT put any number higher than 255
version: tuple[int, int, int] = (0, 4, 0)

compatibility: dict[tuple[int, int, int], VersionCompatibility] = {
    (0, 4, 0): VersionCompatibility((0, 4, 0), (0, 4, 0), (0, 4, 0), (0, 4, 0), (0, 6, 3)),
    (0, 3, 999): VersionCompatibility((0, 3, 99), (0, 3, 0), (0, 3, 200), (0, 3, 6), (0, 6, 3)),
    (0, 3, 99): VersionCompatibility((0, 3, 99), (0, 3, 0), (0, 3, 99), (0, 3, 6), (0, 6, 3)),
    (0, 3, 13): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 13), (0, 3, 13), (0, 6, 3)),
    (0, 3, 12): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 12), (0, 3, 9), (0, 6, 3)),
    (0, 3, 11): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 9), (0, 3, 9), (0, 6, 3)),
    (0, 3, 10): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 9), (0, 3, 9), (0, 6, 3)),
    (0, 3, 9): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 9), (0, 3, 9), (0, 6, 3)),
    (0, 3, 8): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 4), (0, 3, 6), (0, 6, 3)),
    (0, 3, 7): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 4), (0, 3, 6), (0, 6, 3)),
    (0, 3, 6): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 4), (0, 3, 6), (0, 6, 3)),
    (0, 3, 5): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 4), (0, 3, 2), (0, 6, 3)),
    (0, 3, 4): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 4), (0, 3, 2), (0, 6, 3)),
    (0, 3, 3): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 3), (0, 3, 2), (0, 6, 3)),
    (0, 3, 2): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 2), (0, 3, 2), (0, 6, 3)),
    (0, 3, 1): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 0), (0, 3, 0), (0, 6, 3)),
    (0, 3, 0): VersionCompatibility((0, 3, 0), (0, 3, 0), (0, 3, 0), (0, 3, 0), (0, 6, 3)),
}


def patch_file() -> tuple[int, int, int]:
    return compatibility[version].patch_file


def patch_accept(found: tuple[int, ...]) -> int:
    """0 = accepted, 1 = too new, -1 = too old"""
    if found > compatibility[version].patch_file:
        return 1
    elif found < compatibility[version].patch_accept:
        return -1
    else:
        return 0


def rom() -> tuple[int, int, int]:
    return compatibility[version].rom


def ut() -> tuple[int, int, int]:
    return compatibility[version].ut


def ap_minimum() -> tuple[int, int, int]:
    return compatibility[version].ap_minimum


if __name__ == "__main__":
    import orjson, os, zipfile
    from worlds.Files import container_version

    apworld = "pokemon_bw"
    dev_dir = "D:/Games/Archipelago/custom_worlds/dev/"

    with (zipfile.ZipFile(dev_dir + apworld + "_without_maps.apworld", "w", zipfile.ZIP_DEFLATED, True, 9) as zipf,
          zipfile.ZipFile(dev_dir + apworld + ".apworld", 'w', zipfile.ZIP_DEFLATED, True, 9) as zipf2):
        metadata = {
            "game": "Pokemon Black and White",
            "minimum_ap_version": ".".join(str(i) for i in ap_minimum()),
            "authors": ["BlastSlimey", "SparkyDaDoggo"],
            "world_version": ".".join(str(i) for i in version),
            "version": container_version,
            "compatible_version": 7,
        }
        zipf.writestr(os.path.join(apworld, "archipelago.json"), orjson.dumps(metadata))
        zipf2.writestr(os.path.join(apworld, "archipelago.json"), orjson.dumps(metadata))
        for root, dirs, files in os.walk("../"):
            if "__pycache__" in root:
                continue
            for file in files:
                zipf2.write(os.path.join(root, file),
                            os.path.relpath(os.path.join(root, file),
                                            "../../"))
            if "images" in root and not root.endswith("images"):
                continue
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           "../../"))
