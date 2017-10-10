class DebugMetadata:
    def __init__(self):
        self.start_ln = 0
        self.end_ln = 0
        self.file_name = None
        self.source_name = None

    def __str__(self):
        if self.file_name:
            return "line %d of %s" % self.start_line_number, self.file_name
        else:
            return "line %d" % self.start_line_number
