import argparse
import shutil
import pathlib
import numpy as np
import tqdm
from config import SYSTEMS as system_df
from libretro_finder.utils import recursive_hash
 
def organize(directory: pathlib.Path, output_dir: pathlib.Path, glob: str = "*", overwrite=False) -> None:
    """
    Non-destructive function that finds, copies and refactors files to the format expected by libretro (and its cores). This is useful if you source your BIOS files from many different places and have them saved them under different names (often with duplicates). It     
    
    :param directory:
    :param output_dir:
    :param glob:
    :param overwrite:
    :return:
    """
    
    # Indexing files to be checked for matching MD5 checksums
    output_dir.mkdir(parents=True, exist_ok=True)
    file_paths, file_hashes = recursive_hash(directory=directory, glob=glob)

    # Different cores for the same system can use the same BIOS under different names (but with the same MD5 hash)
    # That is why we also search output_dir (i.e. finds all aliases; likely if ran with directory=./system)
    temp_paths, temp_hashes = recursive_hash(directory=output_dir, glob=glob)
    file_paths += temp_paths 
    file_hashes += temp_hashes
    file_paths = np.array(file_paths)
    file_hashes = np.array(file_hashes)
    comparisons = np.equal(
        file_hashes.reshape(1, -1), 
        system_df['md5'].values.reshape(-1, 1)
        )
    
    # If a single core has multiple matches, we just pick the first one (see doc for return_index)    
    system_indices, file_indices = np.where(comparisons)
    _, indices = np.unique(system_indices, return_index=True)
    system_subset = system_df.loc[system_indices[indices]]
    srcs = file_paths[file_indices[indices]]
    assert system_subset['name'].unique().size == system_subset['name'].size
    assert np.unique(srcs).size != srcs.size
    
    # printing matches per system
    matches = system_subset.groupby('system').count()
    n_matches = matches['name'].sum()
    n_systems = matches.shape[0]
    print(f"{n_matches} matching BIOS files were found for {n_systems} unique systems:")
    for name, row in matches.iterrows():
        print(f"\t{name} ({row['name']})")
    
    # copying matching files to output_dir using structure specified by libretro (and expected by libretro cores) 
    dsts = system_subset['name'].values
    for i in tqdm.tqdm(range(srcs.size), total= srcs.size):
        dst = output_dir / dsts[i]
        parent = dst.parent
        if dst.exists() and not overwrite:
            # if file already exists but doesn't match the known checksum, it's likely modified or renamed manually  
            if srcs[i] != system_subset['md5'].values[i]:
                print(f"(!) The file '{srcs[i]}' is likely modified but but will not be replaced (check manually or consider the Overwrite option).")
            continue 
        elif srcs[i] == dst:
            continue
        elif parent != output_dir:
            parent.mkdir(parents=True, exist_ok=True) 
        shutil.copy(src=srcs[i], dst=dst)
                    
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI that finds, copies and refactors BIOS files to the format expected by libretro (and its cores).",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("search_dir", help="Directory to look for BIOS files", type = str)
    parser.add_argument("output_dir", help="Directory to copy found BIOS files to", type = str)
    parser.add_argument("-g", "--glob", help="Glob pattern to use for file matching", type = str, default="*")
    parser.add_argument("-o", "--overwrite", help="Overwrite output", action="store_true")
    args = vars(parser.parse_args())

    directory = pathlib.Path(args["search_dir"])
    output_dir = pathlib.Path(args["output_dir"])
    glob = args["glob"]
    overwrite = args["overwrite"]

    organize(
        directory=directory,
        output_dir=output_dir,
        glob=glob, 
        overwrite=overwrite
        )