class Task:
    def __init__(self,name,priority="中"):

        self.name = name
        self.completed = False
        self.priority = priority


    def complete(self):
        self.completed = True


    def rename(self,new_name):
        self.name = new_name


    def to_dict(self):
        return{ 
            "name": self.name,
            "completed": self.completed,

            "priority": self.priority
        }


    @classmethod
    def from_dict(cls,data):
        priority = data.get("priority","中")

        task = cls(data["name"],priority)
        task.completed = data["completed"]

        return task