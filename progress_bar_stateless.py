import os
import json
import sys
from config_reader import read_image

STATE_FILE = 'progress_bar_state.json'
STATE_FILE_DIRECTORY = '/tmp/ffpi/'

def create_progress_bar(progress_bar_name: str, progress: float=0.0, style: str = 'default') -> None:
    """
    Create a progress bar instance with the given name and style.

    Args:
        name (str): The name of the progress bar.
        style (str): The style of the progress bar.

    Returns:
        ProgressBar: An instance of ProgressBar with specified configurations.
    """
    bar = {
        "progress_bars": { 
            "name": progress_bar_name,
            "progress": progress,
            "style": style
        }
    }

    # ensure directory exists
    os.makedirs(STATE_FILE_DIRECTORY, exist_ok=True)

    existing_data = []
    # Check if the state file exists and load existing data
    try:
        with open(STATE_FILE_DIRECTORY + STATE_FILE, 'r') as f:
            existing_data = json.load(f)
            if type(existing_data) is dict:
                existing_data = [existing_data]
    except FileNotFoundError:
        existing_data = {}

    # Prevent duplicate progress bar names
    for progress_bar in existing_data:
        if progress_bar["name"] == progress_bar_name:
            return # Progress bar with this name already exists
        
    # Append the new progress bar data
    if existing_data:
        existing_data.append(bar["progress_bars"])
        bars = existing_data
    else: # First progress bar being created
        bars = bar["progress_bars"]
    # Write the updated data back to the state file
    with open(STATE_FILE_DIRECTORY + STATE_FILE, 'w') as f:
        json.dump(bars, f, indent=4)


def update_progress_bar(progress_bar_name: str, progress: float) -> None:
    """
    Update the progress of the progress bar with the given name.

    Args:
        name (str): The name of the progress bar.
        progress (float): The current progress (0.0 to 1.0).
    """
    try:
        with open(STATE_FILE_DIRECTORY + STATE_FILE, 'r') as f:
            json_data = json.load(f)
        for bar in json_data:
            if bar["name"] == progress_bar_name:
                bar["progress"] = progress

            with open(STATE_FILE_DIRECTORY + STATE_FILE, 'w') as f:
                json.dump(json_data, f, indent=4)
    except FileNotFoundError:
        raise FileNotFoundError("Progress bar state file not found. Please create a progress bar first.")
    
    __display_progress_bar()

    

def __display_progress_bar() -> None:
    """
    Display the progress bar with the given name and style.

    Args:
        name (str): The name of the progress bar.
        style (str): The style of the progress bar.
    """
    try:
        with open(STATE_FILE_DIRECTORY + STATE_FILE, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Progress bar state file not found. Please create a progress bar first.")
        
    
    lines = []
    for progress_bar in json_data:
        if progress_bar["style"] != 'default':
            raise NotImplementedError("Only 'default' style is implemented.")
            # implemented something like this ----------------
            # read_image(name, "head")
            # read_image(name, "body")
            # read_image(name, "empty")
            # ------------------------------------------------

        default_length = 40
        filled_length = int(progress_bar["progress"] * default_length)
        bar = '█' * filled_length + '-' * (default_length - filled_length)
        percent = progress_bar["progress"] * 100

        line = f'{progress_bar["name"]:<12} |{bar}| {percent:6.2f}%'
        lines.append(line)

        if progress_bar["progress"] >= 1.0:
            sys.stdout.write(f"\033[F")
            sys.stdout.flush()
            lines.remove(line)
            delete_progress_bar(progress_bar["name"])
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
        with open(STATE_FILE_DIRECTORY + STATE_FILE, 'r') as f:
            json_data = json.load(f)
        json_data = [bar for bar in json_data if bar["name"] != progress_bar_name]
        if json_data is not None:
            with open(STATE_FILE_DIRECTORY + STATE_FILE, 'w') as f:
                json.dump(json_data, f)
        else:
            os.remove(STATE_FILE_DIRECTORY + STATE_FILE)     
        
    
    except FileNotFoundError:
        raise FileNotFoundError("Progress bar state file not found. Nothing to delete.")

def clean_up_progress_bars() -> None:
    """
    Clean up all progress bar state files.
    """
    try:
        if os.path.exists(STATE_FILE_DIRECTORY + STATE_FILE):
            os.remove(STATE_FILE_DIRECTORY + STATE_FILE)
    except Exception as e:
        print(f"Error cleaning up progress bars: {e}")

if __name__ == "__main__":
    # Example usage
    import time
    create_progress_bar("Processing")
    create_progress_bar("AnotherBar")
    with open(STATE_FILE_DIRECTORY + STATE_FILE, 'r') as f:
        existing_data = json.load(f)
        # print(existing_data)
    print("Starting progress bars...")
    total_steps = 20
    for step in range(total_steps + 1):
        progress = step / total_steps
        update_progress_bar("Processing", progress)
        update_progress_bar("AnotherBar", progress * 3)
        if step == step // 2 and step != 0:
            create_progress_bar("AnotherAnotherBar")
        if step >= total_steps // 2:
            update_progress_bar("AnotherAnotherBar", (step - total_steps // 2) / (total_steps // 2))
        time.sleep(0.1)  # Simulate work being done
    delete_progress_bar("Processing")
    delete_progress_bar("AnotherBar")
    delete_progress_bar("AnotherAnotherBar")
    clean_up_progress_bars()