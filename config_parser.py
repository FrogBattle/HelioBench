import yaml

EXPERIMENT_CONFIG_FILE_PATH = "./experiment.yml"
PROMETHEUS_CONFIG_FILE_PATH = "./microservices/prometheus/prometheus.yml"

class ConfigError(Exception):
    def __init__(self, message="Error validating config"):
        self.message = message
        super().__init__(self.message)


def parse_config(config_path):
    with open(config_path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def save_config(config_path, config_object):
    with open(config_path, "w") as stream:
        try:
            return yaml.safe_dump(config_object, stream)
        except yaml.YAMLError as exc:
            print(exc)


def validate_config(config):
    if 'services' not in config or len(config['services']) <= 0:
        raise ConfigError("No experiment services specified.")
    if type(config['services']) != type({}):
        raise ConfigError("Experiment services must be a dictionary.")
    for service_name, service in config['services'].items():
        if service is not None:
            if type(service) != type({}):
                raise ConfigError(f"Experiment service {service_name} must be a dictionary.")
            if 'environment' in service:
                if type(service['environment']) != type(list()):
                    raise ConfigError(f"Environment of service {service_name} must be a list.")
    
    return config

def parse_and_validate_config(config_path = EXPERIMENT_CONFIG_FILE_PATH):
    return validate_config(parse_config(config_path))

def parse_variables(variables):
    return {envvar.split('=')[0]:envvar.split('=')[1] for envvar in variables}

def parse_service_envvars(config):
    res = {}
    for service, service_conf in config['services'].items():
        if service_conf is None:
            res[service] = None
        elif 'variables' in service_conf:
            res[service] = parse_variables(service_conf['variables'])

    return res

def parse_environment(config):
    env = config.get('environment', None)
    if env is not None:
        env = parse_variables(env)
    return env

if __name__ == '__main__':
    print(parse_config('./experiment.yml'))