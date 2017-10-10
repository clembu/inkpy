class StoryError(Exception):
    def __init__(self, msg, useln=0):
        super().__init__(msg)
        self.useln = useln
