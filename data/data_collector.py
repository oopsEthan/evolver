import json
import copy
import matplotlib.pyplot as plt
from utilities.config import *

# TODO: Refactor this sh*t

class Data_Collector():
    def __init__(self):
        self.data = []

        self.graph_data = {
            "ticks": [],
            "avg_calories": [],
            "avg_hydration": [],
            "avg_dobamine": [],
            "avg_age": [],
            "avg_food_security": [],
            "avg_water_security": [],
            "alive": [],
            "births": [],
            "deaths": [],
            "starvation": [],
            "dehydration": [],
            "age": []
        }

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
                "females": 0.0,
                "males": 0.0
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

        self.get_metrics(total)
        self.get_graph_data(tick)

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

    # Gets the average stats of a dob, keys must be int
    def get_average_stats(self) -> dict:
        keys = ["calories", "hydration", "dobamine", "age", "food_security", "water_security"]
        totals = {key: 0 for key in keys}

        for dob in ACTIVE_DOBS:
            stats = dob.collect_stats()
            for key in keys:
                totals[key] += stats[key]
            
        count = len(ACTIVE_DOBS)
        return {f"avg_{key}": round((totals[key] / count), 1) for key in keys} if count > 0 else {}
    
    def get_average_exploration_mode(self) -> dict:
        passives = 0
        aggressives = 0

        for dob in ACTIVE_DOBS:
            stats = dob.collect_stats()

            if stats["exploration_mode"] == PASSIVE:
                passives += 1
            
            elif stats["exploration_mode"] == AGGRESSIVE:
                aggressives += 1

        if passives > aggressives: return PASSIVE
        elif aggressives > passives: return AGGRESSIVE
    
        return "balanced"
    
    
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
                "females": round(females / (males + females), 1),
                "males": round(males / (males + females), 1)
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

    def get_metrics(self, total):
        self.metrics["total"] = total
        self.metrics["alive"] = len(ACTIVE_DOBS)
        self.metrics["births"] = total - STARTING_DOB_POPULATION
        self.metrics["death"] = self.get_death_metrics()
        self.metrics["averages"] = self.get_average_stats()
        self.metrics["averages"].update({"avg_exploration_mode": self.get_average_exploration_mode()})
        self.metrics["sex"] = self.get_sex_stats()

    def get_graph_data(self, tick):
        self.graph_data["ticks"].append(tick)
        self.graph_data["alive"].append(self.metrics["alive"])
        self.graph_data["births"].append(self.metrics["births"])

        death_metrics = ["deaths", "starvation", "dehydration", "age"]
        for key in death_metrics:
            self.graph_data[key].append(self.metrics["death"][key])

        average_metrics = ["avg_calories", "avg_hydration", "avg_dobamine", "avg_age", "avg_food_security", "avg_water_security"]
        for key in average_metrics:
            self.graph_data[key].append(self.metrics["averages"].get(key, 0))
    
    def plot_stats(self):
        stats_to_plot = [
            ("avg_calories", "Average Calories"),
            ("avg_hydration", "Average Hydration"),
            ("avg_dobamine", "Average Dobamine"),
            ("avg_age", "Average Age"),
            ("alive", "Alive Dobs"),
            ("births", "Total Births")
        ]

        for stat_key, label in stats_to_plot:
            plt.figure(figsize=(8, 4))
            plt.plot(self.graph_data["ticks"], self.graph_data[stat_key], label=label)
            plt.xlabel("Tick")
            plt.ylabel(label)
            plt.title(f"{label} Over Time")
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(f"data/charts/{stat_key}_over_time.png")
            plt.close()
    
    def plot_death_causes(self):
        plt.figure(figsize=(10, 5))

        plt.plot(self.graph_data["ticks"], self.graph_data["deaths"], label="Total Deaths", linewidth=2)
        plt.plot(self.graph_data["ticks"], self.graph_data["starvation"], label="Starvation", linestyle="--")
        plt.plot(self.graph_data["ticks"], self.graph_data["dehydration"], label="Dehydration", linestyle="--")
        plt.plot(self.graph_data["ticks"], self.graph_data["age"], label="Old Age", linestyle="--")

        plt.xlabel("Tick")
        plt.ylabel("Cumulative Deaths")
        plt.title("Dob Deaths by Cause Over Time")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("data/charts/death_cause_comparison.png")
        plt.close()
    
    def plot_resource_security(self):
        plt.figure(figsize=(10, 5))

        plt.plot(self.graph_data["ticks"], self.graph_data["avg_water_security"], label="Average Water Security", linewidth=2)
        plt.plot(self.graph_data["ticks"], self.graph_data["avg_food_security"], label="Average Food Security", linestyle="--")

        plt.xlabel("Tick")
        plt.ylabel("Average Resource Security")
        plt.title("Resource Security Over Time")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("data/charts/resource_security_comparison.png")
        plt.close()
    
    def plot_alive_vs_food_security(self):
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # First axis: Alive dobs
        ax1.set_xlabel("Tick")
        ax1.set_ylabel("Alive Dobs", color="tab:blue")
        ax1.plot(self.graph_data["ticks"], self.graph_data["alive"], label="Alive", color="tab:blue")
        ax1.tick_params(axis='y', labelcolor="tab:blue")

        # Second axis: Food Security on a different scale
        ax2 = ax1.twinx()
        ax2.set_ylabel("Avg Food Security", color="tab:green")
        ax2.plot(self.graph_data["ticks"], self.graph_data["avg_food_security"], label="Food Security", color="tab:green")
        ax2.tick_params(axis='y', labelcolor="tab:green")

        fig.tight_layout()
        plt.title("Alive Dobs vs. Food Security")
        plt.savefig("data/charts/alive_vs_food_security.png")
        plt.close()