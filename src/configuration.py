import ruamel.yaml

yaml = ruamel.yaml.YAML()

class Configuration():
    def __init__(self):
        
        self.data = None
    def read_yaml(self,filename='configuration.yaml'):
        with open(filename,'r') as stream:
            try:
                self.data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
    def write_yaml(self,outpath='./configuration.yaml'):
        with open(outpath, 'w') as f:
            yaml.dump(self.data, f)
    def overwrite_vc(self,coordinates=[[1,2,3,4],[5,6,7,8]]):
        """coordinates: array [[automac],[street]]"""
        # automac update:
        keyword = 'automac_coordinates'
        if keyword not in self.data['restaurant']['vehicle_counting'].keys():
            raise Exception(f'{keyword} not in yaml file')
        else:
            self.data['restaurant']['vehicle_counting'][keyword].clear()
            for coordinate in coordinates[0]:
                self.data['restaurant']['vehicle_counting'][keyword].append(coordinate)
        # street update:
        keyword = 'street_coordinates'
        if keyword not in self.data['restaurant']['vehicle_counting'].keys():
            raise Exception(f'{keyword} not in yaml file')
        else:
            self.data['restaurant']['vehicle_counting'][keyword].clear()
            for coordinate in coordinates[1]:
                self.data['restaurant']['vehicle_counting'][keyword].append(coordinate)

       