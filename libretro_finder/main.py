import argparse
import shutil
import pathlib
import numpy as np
import tqdm
from config import SYSTEMS as system_df
from libretro_scraper.utils import recursive_hash


def scrape_bios(directory: pathlib.Path, output_dir: pathlib.Path, glob: str = "*", overwrite=False):
    """

    :param directory:
    :param output_dir:
    :param glob:
    :param overwrite:
    :return:
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    file_paths, file_hashes = recursive_hash(directory=directory, glob=glob)
    file_paths = np.array(file_paths)
    file_hashes = np.array(file_hashes)
    comparisons = np.equal(
        file_hashes.reshape(1, -1), 
        system_df['md5'].values.reshape(-1, 1)
        )
    
    # different cores for the same system can use the same bios file under a different name (but with the same hash)
    # if a single core has multiple matches, we just pick the first one (see doc for return_index)
    system_indices, file_indices = np.where(comparisons)
    _, indices = np.unique(system_indices, return_index=True)
    assert np.unique(system_df.loc[system_indices[indices], 'name']).size == system_df.loc[system_indices[indices], 'name'].size
    assert file_paths[file_indices[indices]].size != np.unique(file_paths[file_indices[indices]]).size
    
    # printing matches per system
    matches = system_df.loc[system_indices[indices]].groupby('system').count()
    n_matches = matches['name'].sum()
    n_systems = matches.shape[0]
    print(f"{n_matches} matching BIOS files were found for {n_systems} unique systems:")
    for name, row in matches.iterrows():
        print(f"\t{name} ({row['name']})")
    
    # copying matching files to output_dir using structure specified by libretro (and expected by libretro cores) 
    srcs = file_paths[file_indices[indices]]
    dsts = system_df.loc[system_indices[indices], 'name'].values
    for i in tqdm.tqdm(range(srcs.size), total= srcs.size):
        dst = output_dir / dsts[i]
        dst.mkdir(parents=True, exist_ok=True)        
        if dst.exists() and not overwrite:
            continue
        shutil.copy(src=srcs[i], dst=dst)            
            
if __name__ == "__main__":
    # TODO check file permissions
    # TODO show missing, system status/system support system_df.iloc[~system_indices]
    # TODO Default output_dir to retroarch's system folder
    # TODO implement caching with redis (recursive_hash)

    parser = argparse.ArgumentParser(description="Local BIOS file scraper for Retroarch",
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
    

    # overwrite = True
    # directory = pathlib.Path(r"D:\Games\Roms")
    # glob = "*"
    # output_dir = pathlib.Path(r"D:\Games\Roms\biostest")

    scrape_bios(
        directory=directory,
        output_dir=output_dir,
        glob=glob, 
        overwrite=overwrite
        )