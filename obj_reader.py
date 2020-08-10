from .model import Model

class ObjectReader(object):
    def __init__(self):
        pass

    def read(self, path):
        model = Model()
        with open(path, 'rb') as f:
            model.read(f)

        return model

