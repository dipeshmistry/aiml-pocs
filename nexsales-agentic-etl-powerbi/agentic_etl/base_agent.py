class BaseAgent:
    def __init__(self, name, priority):
        self.name = name
        self.priority = priority

    def fetch(self, primary_row, field_name):
        raise NotImplementedError("Each agent must implement fetch method")
