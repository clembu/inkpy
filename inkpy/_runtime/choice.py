from .object import Object


class Choice(Object):

    # Constructor
    def __init__(self, cp=None):
        self.choicepoint = cp
        self.threadatgen = None
        self.org_thread_idx = 0
        self.org_choice_path = None
        self.text = None
        self.idx = 0

    # Properties

    @property
    def path_str(self):
        return self.choicepoint.path_str

    @property
    def src_path(self):
        return self.choicepoint.path.comps_str

    # Methods
