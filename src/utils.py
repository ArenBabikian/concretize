
from pathlib import Path


def get_and_validate_map_file(map_name, map_dir):
    map_path = Path(f'{map_dir}/{map_name}.xodr')
    if not map_path.exists():
        files = [file.stem for file in Path(map_dir).iterdir() if file.is_file() and file.suffix == '.xodr']
        raise Exception(f"Map <{map_name}> not found. Please select among the following maps: {files}")

    return str(map_path)



