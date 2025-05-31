from config import *

class Brain():
    def __init__(self):
        self.dob = None

        self.needs = [
            WATER,
            FOOD
            # "reproduction"
        ]

        self.prioritized_thinking = [
            ("pursue", lambda dob: any(m["type"] == "need" and dob.check_needs(m["need_type"]) for m in self.short_term_memory["visible"])),
            ("wander", lambda dob: True),
        ]

        self.short_term_memory = {
            "visible": []
        }

        self.long_term_memory = []

    def think(self, dob):
        highest_value_need = self.dob.evaluate_state
        
        for thought, condition in self.prioritized_thinking:
            if condition(dob):
                if not thought == "wander":
                    print(f"Dob #{dob.id} chose to '{thought}'")
                getattr(dob, thought)()
                return

    def memorize(self, dob, target_memory, memory):
        already_seen = any(m["object"] == memory["object"] for m in self.short_term_memory["visible"])

        if target_memory == "short" and not already_seen:
            memory["age"] = DOB_TRAITS["SHORT_TERM_AGE"]
            self.short_term_memory["visible"].append(memory)
        
            print(f"Dob #{dob.id} memorized {memory['object'].get_grid_coordinates()}!")

    def forget(self):
        for memory in self.short_term_memory["visible"]:
            memory["age"] -= 1
        
        self.short_term_memory["visible"] = [memory for memory in self.short_term_memory["visible"] if memory["age"] > 0]

    def evaluate_state(self):
        for need in self.needs:
            if self.dob.check(need):
                for memory in self.short_term_memory:
                    if need == self.short_term_memory["object"].object_tag:
                        return need
        
        return None