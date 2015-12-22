from babbage import CubeManager
from babbage_fiscal import ModelRegistry

class OSCubeManager(CubeManager):

    def __init__(self,engine):
        super(OSCubeManager, self).__init__(engine)
        self.registry = ModelRegistry(engine)

    def list_cubes(self):
        """ List all available models in the DB """
        for instance in self.registry.list_models():
            yield instance

    def has_cube(self, name):
        """ Check if a cube exists. """
        return self.registry.has_model(name)

    def get_cube_model(self, name):
        return self.registry.get_model(name)
