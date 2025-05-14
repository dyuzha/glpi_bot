class GLPIUser:
    def __init__(self, **kwargs):
        self.login = kwargs['1']
        self.id = kwargs['2']
        self.organisation = kwargs['3']

    def get_id(self):
        return self.id
