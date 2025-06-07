import json
import copy
from utilities.config import ACTIVE_DOBS, DOB, STARTING_DOB_POPULATION, FEMALE

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
            },
            "averages": {
                "avg_calories": 0,
                "avg_hydration": 0,
                "avg_dobamine": 0,
                "avg_age": 0
            },
            "sex": {
                "perc_females": 0.0,
                "perc_males": 0.0
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
    def generate_snapshot(self, tick):
        print(f"Generating a snapshot at tick {tick}...")
        total = len(ACTIVE_DOBS) + self.metrics["death"]["deaths"]

        self.metrics["total"] = total
        self.metrics["alive"] = len(ACTIVE_DOBS)
        self.metrics["births"] = total - STARTING_DOB_POPULATION
        self.metrics["death"] = self.get_death_metrics()
        self.metrics["averages"] = self.get_average_stats()
        self.metrics["sex"] = self.get_sex_stats()

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

    def get_average_stats(self) -> dict:
        keys = ["calories", "hydration", "dobamine", "age"]
        totals = {key: 0 for key in keys}

        for dob in ACTIVE_DOBS:
            stats = dob.collect_stats()
            for key in keys:
                totals[key] += stats[key]
            
        count = len(ACTIVE_DOBS)
        return {f"avg_{key}": round((totals[key] / count), 1) for key in keys} if count > 0 else {}
    
    def get_sex_stats(self) -> dict:
        females = 0
        males = 0

        for dob in ACTIVE_DOBS:
            if dob.sex == FEMALE:
                females += 1
            else:
                males += 1

        if females > 0 and males > 0:
            return {
                "females": females / (males + females),
                "males": males / (males + females)
            }
        
        elif males > 0 and females == 0:
            return {
                "males": 1
            }

        elif females > 0 and males == 0:
            return {
                "females": 1
            }
        
        return {}