class AutoIncrementor:
    def __init__(self):
        self.counter = 0

    def get(self) -> str:
        self.counter = self.counter + 1

        return chr(self.counter)


AI = AutoIncrementor()
