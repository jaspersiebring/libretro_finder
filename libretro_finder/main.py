import shutil
import pathlib
from typing import List, Optional
import numpy as np
from gooey import Gooey, GooeyParser  # type: ignore
from config import SYSTEMS as system_df
from config import RETROARCH_PATH
from libretro_finder.utils import match_arrays, recursive_hash


def organize(search_dir: pathlib.Path, output_dir: pathlib.Path) -> None:
    """
    Non-destructive function that finds, copies and refactors files to the format expected by
    libretro (and its cores). This is useful if you source your BIOS files from many different
    places and have them saved them under different names (often with duplicates).

    :param search_dir: starting location of recursive search
    :param output_dir: path to output directory (will be created if it doesn't exist)
    """

    # Indexing files to be checked for matching MD5 checksums
    output_dir.mkdir(parents=True, exist_ok=True)
    file_paths, file_hashes = recursive_hash(directory=search_dir)

    # Element-wise matching of files against libretro's files
    matching_values, file_indices, system_indices = match_arrays(
        array_a=file_hashes, array_b=np.array(system_df["md5"].values)
    )

    if not np.size(matching_values) > 0:
        print("No matching BIOS files were found, exiting..")
        return

    # If a single core has multiple matches, we just pick the first one
    _, indices = np.unique(system_indices, return_index=True)
    srcs = file_paths[file_indices[indices]]
    hashes = file_hashes[file_indices[indices]]
    system_subset = system_df.loc[system_indices[indices]]

    # np.unique and indexing doesn't merit a dedicated function but it should still be tested
    assert np.array_equal(np.array(system_subset["md5"].values), hashes)
    assert system_subset["name"].size == system_subset["name"].unique().size

    # printing matches per system
    matches = system_subset.groupby("system").count()
    print(
        f"{matches['name'].sum()} matching BIOS files were found for {matches.shape[0]} "
        "unique systems:"
    )
    for name, row in matches.iterrows():
        print(f"\t{name} ({row['name']})")

    # copying matching files to output_dir using structure specified by libretro
    dsts = system_subset["name"].values

    # checking whether our input and output paths are of equal length
    assert len(srcs) == len(dsts)

    for i in range(srcs.size):
        dst = output_dir / dsts[i]
        parent = dst.parent
        if dst.exists() or srcs[i] == dst:
            continue
        if parent != output_dir:
            parent.mkdir(parents=True, exist_ok=True)

        shutil.copy(src=srcs[i], dst=dst)


@Gooey(program_name="LibretroFinder", default_size=(610, 530), required_cols=1)
def main(argv: Optional[List[str]] = None) -> None:
    """
    A simple command line utility that finds and prepares your BIOS files for all documented
    RetroArch cores. If called without any arguments, a simple graphical user interface with
    the same functionality will be started (courtesy of Gooey).
    """

    parser = GooeyParser(
        description="Locate and prepare your BIOS files for libretro.",
    )
    parser.add_argument(
        "Search directory",
        help="Where to look for BIOS files",
        type=pathlib.Path,
        widget="DirChooser",
    )
    parser.add_argument(
        "Output directory",
        help="Where to output refactored BIOS files (defaults to ./retroarch/system)",
        type=pathlib.Path,
        widget="DirChooser",
        default=str(RETROARCH_PATH) if RETROARCH_PATH else None,
    )
    args = vars(parser.parse_args(argv))

    search_directory = args["Search directory"]
    output_directory = args["Output directory"]

    if not search_directory.exists():
        raise FileNotFoundError("Search directory does not exist..")
    if not search_directory.is_dir():
        raise NotADirectoryError("Search directory needs to be a directory..")

    organize(search_dir=search_directory, output_dir=output_directory)


if __name__ == "__main__":
    main()
