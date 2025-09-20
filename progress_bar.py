import typing
from typing import Generator

class ProgressBar:
    def __init__(self, desc: str, total: int, bar_length: int = 40):
        self.desc = desc
        self.total = total
        self.bar_length = bar_length
        self.current = 0

    def update(self, step: int):
        self.current = step
        filled_length = int(self.bar_length * self.current // self.total)
        bar = '█' * filled_length + '-' * (self.bar_length - filled_length)
        percent = (self.current / self.total) * 100
        print(f'\r{self.desc} |{bar}| {percent:.2f}% Complete', end='\r')
        if self.current == self.total:
            print()  # Move to the next line on completion

def progress_bar(desc: str, total: int, current: int = 0) -> Generator[int, None, None]:
    """
    A generator function that yields the current step and updates the progress bar.

    Args:
        desc (str): Description of the progress bar.
        total (int): Total number of steps.
        current (int): Current step to start from.

    Yields:
        int: The current step.
    """
    pb = ProgressBar(desc, total)
    for step in range(current, total + 1):
        pb.update(step)
        yield step

if __name__ == "__main__":
    # Example usage
    import time

    total_steps = 100
    for step in progress_bar("Processing", total_steps):
        time.sleep(0.1)  # Simulate work being done