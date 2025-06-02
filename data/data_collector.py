import json

class Data_Collector():
    def __init__(self):
        self.data_package = []

    def generate_data_file(self):
        self.define_data()
        with open ("simulation_results.json", "w") as f:
            print("Dumping simulation results...")
            json.dump(self.data_package, f, indent=4)
            print("All done!")
    
    def add_data_to_package(self, data):
        self.data_package.append(data)
    
    def define_data(self):
        print("Aggregating data...")
        total_starved = 0
        total_dehydrated = 0
        total_olds = 0

        for entry in self.data_package:
            if entry["cause_of_death"] == "starvation":
                total_starved += 1
            elif entry["cause_of_death"] == "dehydration":
                total_dehydrated += 1
            elif entry["cause_of_death"] == "old_age":
                total_olds += 1

        total = total_starved + total_olds + total_dehydrated

        aggregate = {
            "total_deaths": total,
            "perc_starved": round((total_starved/total) , 2),
            "perc_dehydrated": round((total_dehydrated/total), 2),
            "perc_olds": round((total_olds/total), 2),
        }

        self.data_package.insert(0, aggregate)