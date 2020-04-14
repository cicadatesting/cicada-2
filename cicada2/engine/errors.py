# TODO: move to shared
class ValidationError(AssertionError):
    def __init__(self, *args):
        super(ValidationError, self).__init__(*args)
