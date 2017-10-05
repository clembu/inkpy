from .env import LexEnv


class State:
    def __init__(self, story):
        self.lexenv = LexEnv(None, None)
