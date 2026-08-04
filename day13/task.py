class Task:
    def __init__(self,name):
        self.name = name
        self.completed = False



    def complete(self):
        self.completed = True


    def rename(self,new_name):
        self.name = new_name


    def to_dict(self):
        return{
            "name": self.name,
            "completed": self.completed
        }


    @classmethod
    def from_dict(cls,data):
        task = cls(data["name"])
        task.completed = data["completed"]

        return task