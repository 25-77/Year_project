import yaml

def read_yaml(path):
    with open(path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def get_confg(path, value):
    yaml_file = read_yaml(path)
    return yaml_file[value]
