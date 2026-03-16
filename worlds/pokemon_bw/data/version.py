from typing import NamedTuple


class VersionCompatibility(NamedTuple):
    patch_file: tuple[int, int, int]
    patch_accept: tuple[int, int, int]
    rom: tuple[int, int, int]
    ut: tuple[int, int, int]
    ap_minimum: tuple[int, int, int]


version: tuple[int, int, int] = (0, 3, 24)

compatibility: dict[tuple[int, int, int], VersionCompatibility] = {
    (0, 3, 24): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 23), (0, 3, 24), (0, 6, 4)),
    (0, 3, 23): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 23), (0, 3, 21), (0, 6, 4)),
    (0, 3, 22): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 21), (0, 3, 21), (0, 6, 4)),
    (0, 3, 21): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 21), (0, 3, 21), (0, 6, 4)),
    (0, 3, 20): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 20), (0, 3, 20), (0, 6, 4)),
    (0, 3, 19): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 19), (0, 3, 19), (0, 6, 4)),
    (0, 3, 18): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 18), (0, 3, 18), (0, 6, 3)),
    (0, 3, 17): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 17), (0, 3, 17), (0, 6, 3)),
    (0, 3, 16): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 15), (0, 3, 15), (0, 6, 3)),
    (0, 3, 15): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 15), (0, 3, 15), (0, 6, 3)),
    (0, 3, 14): VersionCompatibility((0, 3, 14), (0, 3, 0), (0, 3, 14), (0, 3, 14), (0, 6, 3)),
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

    (0, 2, 3): VersionCompatibility((0, 2, 0), (0, 2, 0), (0, 2, 3), (0, 2, 1), (0, 6, 3)),
    (0, 2, 2): VersionCompatibility((0, 2, 0), (0, 2, 0), (0, 2, 2), (0, 2, 1), (0, 6, 3)),
    (0, 2, 1): VersionCompatibility((0, 2, 0), (0, 2, 0), (0, 2, 0), (0, 2, 1), (0, 6, 3)),
    (0, 2, 0): VersionCompatibility((0, 2, 0), (0, 2, 0), (0, 2, 0), (0, 2, 0), (0, 6, 3)),

    (0, 1, 7): VersionCompatibility((0, 1, 0), (0, 1, 0), (0, 1, 7), (0, 1, 7), (0, 6, 3)),
    (0, 1, 6): VersionCompatibility((0, 1, 0), (0, 1, 0), (0, 1, 6), (0, 1, 6), (0, 6, 3)),
    (0, 1, 5): VersionCompatibility((0, 1, 0), (0, 1, 0), (0, 1, 5), (0, 1, 4), (0, 6, 3)),
    (0, 1, 4): VersionCompatibility((0, 1, 0), (0, 1, 0), (0, 1, 4), (0, 1, 4), (0, 6, 3)),
    (0, 1, 3): VersionCompatibility((0, 1, 0), (0, 1, 0), (0, 1, 3), (0, 1, 2), (0, 6, 3)),
    (0, 1, 2): VersionCompatibility((0, 1, 0), (0, 1, 0), (0, 1, 2), (0, 1, 2), (0, 6, 3)),
    (0, 1, 1): VersionCompatibility((0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 6, 3)),
    (0, 1, 0): VersionCompatibility((0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 6, 3)),
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


def revert(value: int, dec=True) -> str:
    # Please don't ask about this
    l = []
    while value:
        l.append(value % 256)
        value //= 256
    for i in range(len(l)-1):
        l[i+1] = (l[i+1] - l[i]) % 256
    return bytes(l[:-1]).decode() if dec else bytes(l[:-1])


def stack(value: str) -> int:
    l = 0
    for i in reversed(value.encode()):
        l = l * 256 + i
    l += l*256
    return l


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
