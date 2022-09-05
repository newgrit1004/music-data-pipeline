from pathlib import Path, PosixPath

def makedirs(dir_name:str) -> PosixPath:
    """Generate a new directory and return its folder name.

    Args:
        dir_name (str): directory name

    Returns:
        PosixPath
    """
    new_path = Path(__file__).parents[1] / dir_name
    new_path.mkdir()
    return new_path

