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
            "avg_max_calories": [],       
            "avg_max_hydration": [],      
            "avg_death_age": [],          
            "alive": [],
            "births": [],
            "deaths": [],
            "starvation": [],
            "dehydration": [],
            "age": [],
            "avg_females": [],            
            "avg_males": []               
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
        keys = ["calories", "hydration", "dobamine", "age", # standard stats
                "food_security", "water_security", # resource count stats
                "max_calories", "max_hydration", "death_age"] # mutated stats
        totals = {key: 0 for key in keys}

        for dob in ACTIVE_DOBS:
            stats = dob.collect_stats()
            for key in keys:
                totals[key] += stats[key]
            
        count = len(ACTIVE_DOBS)
        averages = {f"avg_{key}": round((totals[key] / count), 1) for key in keys} if count > 0 else {}

        averages.update(self.get_sex_stats())
        return averages
    
    def get_sex_stats(self) -> dict:
        males = 0
        females = 0

        for dob in ACTIVE_DOBS:
            if dob.sex == FEMALE:
                females += 1
            elif dob.sex == MALE:
                males += 1

        total = males + females

        if total == 0:
            return {"avg_females": 0.0, "avg_males": 0.0}

        return {
            "avg_females": round(females / total, 2),
            "avg_males": round(males / total, 2)
        }


    def get_metrics(self, total):
        self.metrics["total"] = total
        self.metrics["alive"] = len(ACTIVE_DOBS)
        self.metrics["births"] = total - STARTING_DOB_POPULATION
        self.metrics["death"] = self.get_death_metrics()
        self.metrics["averages"] = self.get_average_stats()
        # self.metrics["averages"].update({"avg_exploration_mode": self.get_average_exploration_mode()})
        self.metrics["sex"] = self.get_sex_stats()

    def get_graph_data(self, tick):
        self.graph_data["ticks"].append(tick)
        self.graph_data["alive"].append(self.metrics["alive"])
        self.graph_data["births"].append(self.metrics["births"])

        death_metrics = ["deaths", "starvation", "dehydration", "age"]
        for key in death_metrics:
            self.graph_data[key].append(self.metrics["death"][key])

        average_metrics = average_metrics = [
            "avg_calories", "avg_hydration", "avg_dobamine", "avg_age",
            "avg_food_security", "avg_water_security",
            "avg_max_calories", "avg_max_hydration", "avg_death_age",
            "avg_females", "avg_males"
        ]

        for key in average_metrics:
            self.graph_data[key].append(self.metrics["averages"].get(key, 0))
    
    def plot_stats(self, plot_it: bool):
        stats_to_plot = [
            ("avg_calories", "Average Calories"),
            ("avg_hydration", "Average Hydration"),
            ("avg_dobamine", "Average Dobamine"),
            ("avg_age", "Average Age"),
        ]

        for stat_key, label in stats_to_plot:
            plt.figure(figsize=(8, 4))
            plt.plot(self.graph_data["ticks"], self.graph_data[stat_key], label=label)
            self.plot_it(y_label=label, title=f"{label} Over Time", save=f"data/charts/{stat_key}_over_time.png", plot_it=plot_it)
    
    def plot_death_causes(self, plot_it: bool):
        plt.figure(figsize=(10, 5))
        plt.plot(self.graph_data["ticks"], self.graph_data["deaths"], label="Total Deaths", linewidth=2)
        plt.plot(self.graph_data["ticks"], self.graph_data["starvation"], label="Starvation", linestyle="--")
        plt.plot(self.graph_data["ticks"], self.graph_data["dehydration"], label="Dehydration", linestyle="--")
        plt.plot(self.graph_data["ticks"], self.graph_data["age"], label="Old Age", linestyle="--")
        self.plot_it("Cumulative Deaths", "Dob Deaths by Cause Over Time", "data/charts/death_cause_comparison.png", plot_it=plot_it)

    def plot_resource_security(self, plot_it: bool):
        plt.figure(figsize=(10, 5))
        plt.plot(self.graph_data["ticks"], self.graph_data["avg_water_security"], label="Average Water Security", linewidth=2)
        plt.plot(self.graph_data["ticks"], self.graph_data["avg_food_security"], label="Average Food Security", linestyle="--")
        self.plot_it("Average Resource Security", "Resource Security Over Time", "data/charts/resource_security_comparison.png", plot_it=plot_it)

    def plot_mutation_traits(self, plot_it: bool):
        fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

        ticks = self.graph_data["ticks"]

        axs[0].plot(ticks, self.graph_data["avg_death_age"], label="Avg Death Age", color="tab:red")
        axs[0].set_ylabel("Death Age")
        axs[0].legend()
        axs[0].grid(True)

        axs[1].plot(ticks, self.graph_data["avg_max_calories"], label="Avg Max Calories", color="tab:orange")
        axs[1].set_ylabel("Max Calories")
        axs[1].legend()
        axs[1].grid(True)

        axs[2].plot(ticks, self.graph_data["avg_max_hydration"], label="Avg Max Hydration", color="tab:blue")
        axs[2].set_ylabel("Max Hydration")
        axs[2].set_xlabel("Tick")
        axs[2].legend()
        axs[2].grid(True)

        fig.tight_layout()
        if plot_it:
            fig.suptitle("Dob Mutation Traits Over Time", fontsize=14)
            fig.subplots_adjust(top=0.93)
            plt.savefig("data/charts/mutation_trait_trends.png")
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
    
    def plot_alive_vs_sex_ratio(self):
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Alive count on left Y-axis
        ax1.set_xlabel("Tick")
        ax1.set_ylabel("Alive Dobs", color="tab:blue")
        ax1.plot(self.graph_data["ticks"], self.graph_data["alive"], label="Alive Dobs", color="tab:blue")
        ax1.tick_params(axis='y', labelcolor="tab:blue")

        # Sex ratio on right Y-axis
        ax2 = ax1.twinx()
        ax2.set_ylabel("Female Ratio", color="tab:pink")
        ax2.plot(self.graph_data["ticks"], self.graph_data["avg_females"], label="Female Ratio", color="tab:pink", linestyle="--")
        ax2.tick_params(axis='y', labelcolor="tab:pink")

        fig.tight_layout()
        plt.title("Alive Dobs vs. Female Sex Ratio")
        plt.savefig("data/charts/alive_vs_sex_ratio.png")
        plt.close()

    def plot_births_vs_sex_ratio(self):
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Birth count on left Y-axis
        ax1.set_xlabel("Tick")
        ax1.set_ylabel("Total Births", color="tab:green")
        ax1.plot(self.graph_data["ticks"], self.graph_data["births"], label="Total Births", color="tab:green")
        ax1.tick_params(axis='y', labelcolor="tab:green")

        # Sex ratio on right Y-axis
        ax2 = ax1.twinx()
        ax2.set_ylabel("Female Ratio", color="tab:pink")
        ax2.plot(self.graph_data["ticks"], self.graph_data["avg_females"], label="Female Ratio", color="tab:pink", linestyle="--")
        ax2.tick_params(axis='y', labelcolor="tab:pink")

        fig.tight_layout()
        plt.title("Births vs. Female Sex Ratio")
        plt.savefig("data/charts/births_vs_sex_ratio.png")
        plt.close()

    def plot_it(self, y_label: str, title: str, save: str, plot_it: bool=False):
        if plot_it:
            plt.xlabel("Tick")
            plt.ylabel(y_label)
            plt.title(title)
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(save)
            plt.close()