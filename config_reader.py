import yaml

def read_config(file_path) -> dict:
    """Reads a YAML configuration file and returns its contents as a dictionary."""
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            if isinstance(config, list):
                config = {str(i): v for i, v in enumerate(config)}
        return config
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return {}
    
def read_head(name: str, file_path: str="config.yaml") -> str:
    """Reads a header from a text file and returns it as a string."""
    return read_image(name, "head", file_path)

def read_empty(name: str, file_path: str="config.yaml") -> str:
    """Reads a empty from a text file and returns it as a string."""
    return read_image(name, "empty", file_path)

def read_body(name: str, file_path: str="config.yaml") -> str:
    """Reads a body from a text file and returns it as a string."""
    return read_image(name, "body", file_path)

def read_image(name: str, segment: str, file_path: str="config.yaml") -> str:
    """Reads an ASCII art image from a text file and returns it as a string."""
    image_array = read_config(file_path)[name][segment]
    # add new line characters between lines
    for i in range(len(image_array)):
        image_array[i] += "\n"
    image = "".join(image_array)
    return image

if __name__ == "__main__":
    # Example usage
    print(read_image("train", "head"))