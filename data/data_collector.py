import json
from config import ACTIVE_DOBS, DOB_DB

class Data_Collector():
    def __init__(self):
        self.dob_log = []
        self.data = []

        # Death counters
        self.total_deaths = 0
        self.total_starved = 0
        self.total_dehydrated = 0
        self.total_olds = 0

        # Counters
        self.total_alive = 0
        self.total_births = 0

        self.last_snapshot = {}

        self.save_to_data_file()

    def save_to_data_file(self):
        with open ("simulation_results.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def log_dobs(self):
        for dob in DOB_DB:
            if not dob in self.dob_log:
                self.total_alive += 1
                self.dob_log.append(dob.id)
            
            if dob.offspring > self.dob_log[dob].offspring:
                self.total_births -= self.dob_log[dob].offspring
                self.total_births += dob.offspring

    def log_death(self, dob):
        self.total_deaths += 1
        if dob.cod == "starvation":
            self.total_starved += 1
        elif dob.cod == "dehydration":
            self.total_dehydrated += 1
        elif dob.cod == "age":
            self.total_olds += 1

    def generate_snapshot(self, ticks):
        pass
        snapshot = {
            "ticks": ticks,
            "total_dobs": len(DOB_DB),
            "total_alive": len(ACTIVE_DOBS)
        }

        if total_births > 0:
            snapshot["total_births"] = total_births

        if self.total_deaths > 0:
            snapshot["death"] = {
                "total_deaths": self.total_deaths,
                "perc_starved": round(total_starved / self.total_deaths, 2),
                "perc_dehydrated": round(total_dehydrated / total_deaths, 2),
                "perc_age": round(total_olds / total_deaths, 2),
            }

        if snapshot == self.last_snapshot:
            print("No snapshot, nothing changed...")
            return

        self.last_snapshot = snapshot

        print(f"Generating snapshot at {ticks}...")
        self.data.append(snapshot)
        self.dob_packages = []