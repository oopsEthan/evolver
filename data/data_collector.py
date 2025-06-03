import json
from utilities.config import ACTIVE_DOBS, DOB, STARTING_DOB_POPULATION

class Data_Collector():
    def __init__(self):
        self.data = []

        # Death counters
        self.total_deaths = 0
        self.total_starved = 0
        self.total_dehydrated = 0
        self.total_olds = 0

        # Counters
        self.total_alive = 0
        self.total_births = 0

        self.last_snapshot = {
            "dobs": STARTING_DOB_POPULATION,
        }

        self.save_to_data_file()

    def save_to_data_file(self):
        with open ("simulation_results.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def report(self, target, package):
        if target == DOB:
            self.log_death(package["cause_of_death"])

    def log_death(self, cause_of_death):
        self.total_deaths += 1
        if cause_of_death == "starvation":
            self.total_starved += 1
        elif cause_of_death == "dehydration":
            self.total_dehydrated += 1
        elif cause_of_death == "age":
            self.total_olds += 1

    def generate_snapshot(self):
        snapshot = {
            "dobs": len(ACTIVE_DOBS) + self.total_deaths,
            "total_alive": len(ACTIVE_DOBS)
        }

        if self.total_births > 0:
            snapshot["total_births"] = self.total_births

        if self.total_deaths > 0:
            snapshot["death"] = {
                "total_deaths": self.total_deaths,
                "perc_starved": round(self.total_starved / self.total_deaths, 2),
                "perc_dehydrated": round(self.total_dehydrated / self.total_deaths, 2),
                "perc_age": round(self.total_olds / self.total_deaths, 2),
            }

        if snapshot == self.last_snapshot:
            print("No snapshot, nothing changed...")
            return

        if snapshot["dobs"] > self.last_snapshot["dobs"]:
            self.total_births += snapshot["dobs"] - self.last_snapshot["dobs"]
            snapshot["total_births"] = self.total_births

        self.last_snapshot = snapshot

        self.data.append(snapshot)