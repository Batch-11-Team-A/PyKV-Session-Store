import json
import os
import threading
from typing import Dict, Any


class PersistenceManager:
    """
    Handles saving and loading session data to disk.
    Role 2: Persistence Layer
    """

    def __init__(self, filename: str = "storage.json"):

        self.filename = filename
        self.lock = threading.Lock()

    def save_to_disk(self, data: Dict[str, Any]) -> None:
        """
        Save in-memory data to JSON file
        """

        with self.lock:

            try:
                with open(self.filename, "w") as f:
                    json.dump(data, f, indent=4)

            except Exception as e:
                print(f"[Persistence Error] Save failed: {e}")

    def load_from_disk(self) -> Dict[str, Any]:
        """
        Load data from JSON file
        """

        with self.lock:

            if not os.path.exists(self.filename):
                print("[Persistence] No file found. Starting fresh.")
                return {}

            try:
                with open(self.filename, "r") as f:
                    return json.load(f)

            except json.JSONDecodeError:
                print("[Persistence Error] Corrupted file.")
                return {}

            except Exception as e:
                print(f"[Persistence Error] Load failed: {e}")
                return {}
