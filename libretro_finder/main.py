import argparse
import shutil
import pathlib
import numpy as np
import tqdm

from config import SYSTEMS as system_df
from libretro_finder.utils import match_arrays, recursive_hash

def organize(
    search_dir: pathlib.Path, output_dir: pathlib.Path, glob: str = "*"
) -> None:
    """
    Non-destructive function that finds, copies and refactors files to the format expected by libretro (and its cores).
    This is useful if you source your BIOS files from many different places and have them saved them under different names (often with duplicates).

    :param search_dir:
    :param output_dir:
    :param glob:
    :param overwrite:
    :return:
    """

    # Indexing files to be checked for matching MD5 checksums
    output_dir.mkdir(parents=True, exist_ok=True)
    file_paths, file_hashes = recursive_hash(directory=search_dir, glob=glob)

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

    # np.unique and array subsetting doesn't merit a dedicated function but it should still be tested
    assert np.array_equal(np.array(system_subset["md5"].values), hashes)
    assert system_subset["name"].size == system_subset["name"].unique().size

    # printing matches per system
    matches = system_subset.groupby("system").count()
    print(
        f"{matches['name'].sum()} matching BIOS files were found for {matches.shape[0]} unique systems:"
    )
    for name, row in matches.iterrows():
        print(f"\t{name} ({row['name']})")

    # copying matching files to output_dir using structure specified by libretro (and expected by libretro cores)
    dsts = system_subset["name"].values

    # checking whether our input and output paths are of equal length
    assert len(srcs) == len(dsts)

    for i in tqdm.tqdm(range(srcs.size), total=srcs.size):
        dst = output_dir / dsts[i]
        parent = dst.parent
        if dst.exists() or srcs[i] == dst:
            continue
        elif parent != output_dir:
            parent.mkdir(parents=True, exist_ok=True)

        shutil.copy(src=srcs[i], dst=dst)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CLI that finds, copies and refactors BIOS files to the format expected by libretro (and its cores).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("search_dir", help="Directory to look for BIOS files", type=str)
    parser.add_argument(
        "output_dir", help="Directory to copy found BIOS files to", type=str
    )
    parser.add_argument(
        "-g",
        "--glob",
        help="Glob pattern to use for file matching",
        type=str,
        default="*",
    )
    parser.add_argument(
        "-o", "--overwrite", help="Overwrite output", action="store_true"
    )
    args = vars(parser.parse_args())

    search_directory = pathlib.Path(args["search_dir"])
    output_directory = pathlib.Path(args["output_dir"])
    search_glob = args["glob"]

    organize(search_dir=search_directory, output_dir=output_directory, glob=search_glob)