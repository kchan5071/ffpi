"""
Stateless progress bar implementation using a JSON file for state management.
"""

import os
import json
import sys
import typing
# from config_reader import read_image  # future use for non-default styles

STATE_FILE = "progress_bar_state.json"
STATE_FILE_DIRECTORY = "/tmp/ffpi/"
STATE_FILE_PATH = os.path.join(STATE_FILE_DIRECTORY, STATE_FILE)


def create_progress_bar(
    progress_bar_name: str,
    progress_value: float = 0.0,
    style: str = "default"
) -> None:
    """
    Create a progress bar instance with the given name and style.

    Args:
        name (str): The name of the progress bar.
        style (str): The style of the progress bar.
    """
    progress_bar_data: dict = {
        "progress_bars": {
            "name": progress_bar_name,
            "progress": progress_value,
            "style": style,
        }
    }

    # ensure directory exists
    os.makedirs(STATE_FILE_DIRECTORY, exist_ok=True)

    existing_data: typing.List[typing.Dict[str, typing.Any]] = []
    # Check if the state file exists and load existing data
    try:
        state_file_path = os.path.join(STATE_FILE_DIRECTORY, STATE_FILE)
        with open(state_file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            if isinstance(existing_data, dict):
                existing_data = [existing_data]
    except FileNotFoundError:
        existing_data = []

    # Prevent duplicate progress bar names
    for progress_bar in existing_data:
        if progress_bar["name"] == progress_bar_name:
            return  # Progress bar with this name already exists

    # Append the new progress bar data
    if existing_data:
        existing_data.append(progress_bar_data["progress_bars"])
        bars: list = existing_data
    else:  # First progress bar being created
        bars = [progress_bar_data["progress_bars"]]
    # Write the updated data back to the state file
    with open(STATE_FILE_DIRECTORY + STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(bars, f, indent=4)


def update_progress_bar(progress_bar_name: str, progress_value: float) -> None:
    """
    Update the progress of the progress bar with the given name.

    Args:
        name (str): The name of the progress bar.
        progress (float): The current progress (0.0 to 1.0).
    """
    try:
        with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        for progree_bar_data in json_data:
            if progree_bar_data["name"] == progress_bar_name:
                progree_bar_data["progress"] = progress_value

            with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "Progress bar state file not found. "
            "Please create a progress bar first."
        ) from exc

    __display_progress_bar()


def __display_progress_bar() -> None:
    """
    Display the progress bar with the given name and style.

    Args:
        name (str): The name of the progress bar.
        style (str): The style of the progress bar.
    """
    json_data = []
    try:
        with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "Progress bar state file not found. "
            "Please create a progress bar first."
        ) from exc

    lines: list = []
    # Iterate through all progress bars and build their display lines
    for progress_bar in json_data:
        if progress_bar["style"] != "default":
            raise NotImplementedError("Only 'default' style is implemented.")
            # implemented something like this ----------------
            # read_image(name, "head")
            # read_image(name, "body")
            # read_image(name, "empty")
            # ------------------------------------------------
        default_length = 40
        if progress_bar["progress"] >= 1.0:
            filled_length:  int = default_length
            empty_length:   int = 0
            bar_symbol:     str = "█" * filled_length
            percent:        float = 100.0
        else:
            filled_length = int(progress_bar["progress"] * default_length)
            empty_length = default_length - filled_length
            bar_symbol = "█" * filled_length + "-" * empty_length
            percent = progress_bar["progress"] * 100

        bar_name: str = f"{progress_bar['name']:<20} | "
        bar_body: str = f"{bar_symbol} |"
        bar_tail: str = f" {percent:6.2f}%"
        line: str = f"{bar_name}{bar_body}{bar_tail}"
        lines.append(line)

    # Combine all lines into one string
    output = "\n".join(lines)

    # Print and move cursor up to overwrite next time
    sys.stdout.write(output + "\n")
    sys.stdout.write(f"\033[{len(lines)}F")  # Move cursor up by number of bars
    sys.stdout.flush()


def delete_progress_bar(progress_bar_name: str) -> None:
    """
    Delete the progress bar with the given name.

    Args:
        name (str): The name of the progress bar.
    """
    try:
        with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        json_data = [
            progress_bar_data
            for progress_bar_data in json_data
            if progress_bar_data["name"] != progress_bar_name
        ]
        if json_data is not None:
            with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(json_data, f)
        else:
            os.remove(STATE_FILE_PATH)

    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "Progress bar state file not found. "
            "Nothing to delete."
        ) from exc


def clean_up_progress_bars() -> None:
    """
    Clean up all progress bar state files.
    """
    try:
        if os.path.exists(STATE_FILE_DIRECTORY + STATE_FILE):
            os.remove(STATE_FILE_DIRECTORY + STATE_FILE)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "Progress bar state file not found. "
            "Nothing to clean up."
        ) from exc


if __name__ == "__main__":
    # Example usage
    import time

    create_progress_bar("Processing")
    create_progress_bar("AnotherBar")

    TOTAL_STEPS = 100
    for step in range(TOTAL_STEPS + 1):
        progress = step / TOTAL_STEPS

        update_progress_bar("Processing", progress)
        update_progress_bar("AnotherBar", progress_value=progress * 3)

        # Create a third progress bar halfway through
        if TOTAL_STEPS // 2 == step and step != 0:
            create_progress_bar("AnotherAnotherBar")
        if step >= step // 2:  # update third bar after creation
            update_progress_bar("AnotherAnotherBar", progress * 1.2)

        time.sleep(0.1)  # Simulate work being done
    # delete progress bars after completion
    delete_progress_bar("Processing")
    delete_progress_bar("AnotherBar")
    delete_progress_bar("AnotherAnotherBar")
    clean_up_progress_bars()
