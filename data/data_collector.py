import json
import copy
from utilities.config import ACTIVE_DOBS, DOB, STARTING_DOB_POPULATION

class Data_Collector():
    def __init__(self):
        self.data = []

        # Metrics dictionary
        self.metrics = {
            "total": STARTING_DOB_POPULATION,
            "alive": STARTING_DOB_POPULATION,
            "births": 0,
            "death": {
                "deaths": 0,
                "starvation": 0,
                "dehydration": 0,
                "age": 0
            }
        }

    def save_snapshots_to_file(self):
        with open ("data/simulation_snapshots.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def process_package(self, package: dict) -> None:
        """Processes a data package for the next snapshot"""
        if package["tag"] == DOB:
            self.metrics["death"]["deaths"] += 1
            self.metrics["death"][package["cause_of_death"]] += 1

    # Creates a snapshot of data
    def generate_snapshot(self):
        total = len(ACTIVE_DOBS) + self.metrics["death"]["deaths"]
        births = STARTING_DOB_POPULATION - total

        self.metrics["total"] = total
        self.metrics["alive"] = len(ACTIVE_DOBS)
        self.metrics["births"] = births
        self.metrics["death"] = self.get_death_metrics()

        snapshot = copy.deepcopy(self.metrics)
        if not self.data or snapshot != self.data[-1]:
            self.data.append(snapshot)

    # Returns a snapshot of deaths and causes of death
    def get_death_metrics(self) -> dict:
        deaths = self.metrics["death"]["deaths"]
    
        return {
            "deaths": deaths,
            "starvation": self.metrics["death"]["starvation"],
            "dehydration": self.metrics["death"]["dehydration"],
            "age": self.metrics["death"]["age"],
        }

    # Returns a snapshot of current births