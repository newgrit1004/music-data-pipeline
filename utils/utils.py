import os

def makedirs(current_path:str, dir_name:str) -> str:
    """Generate a new directory and return its folder name.

    Args:
        sound (AudioSegment): an AudioSegment object
        target_dBFS (float): if target_dbFS is lower than 0, the sound will be lowered.
                                Otherwise, the sound will be raised.

    Returns:
        AudioSegment object : raised or lowered determined by target_dBFS
    """
    new_path = os.path.join(current_path, dir_name)
    try:
        os.makedirs(new_path)
    except OSError:
        if not os.path.isdir(new_path):
            raise

    return new_path.split('/')[-1]

