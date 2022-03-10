import re
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
    if not isinstance(config['services'], dict):
        raise ConfigError("Experiment services must be a dictionary.")
    for service_name, service in config['services'].items():
        if service is not None:
            if not isinstance(service, dict):
                raise ConfigError(
                    f"Experiment service {service_name} must be a dictionary.")
            if 'environment' in service:
                if not isinstance(service['environment'], list):
                    raise ConfigError(
                        f"Environment of service {service_name} must be a list.")

    return config


def parse_and_validate_config(config_path=EXPERIMENT_CONFIG_FILE_PATH):
    return validate_config(parse_config(config_path))


def parse_variables(variables, delimiter='='):
    return {envvar.split(delimiter)[0]: delimiter.join(envvar.split(delimiter)[1:]) for envvar in variables}


def parse_service_envvars(config):
    res = {}
    for service, service_conf in config['services'].items():
        if service_conf is None:
            res[service] = None
        elif 'variables' in service_conf:
            res[service] = parse_variables(service_conf['variables'])

    return res


def parse_environment(config):
    env = config.get('environment', {})
    if env is None:
        env = {}
    if len(env) != 0:
        env = parse_variables(env)
    return env


def parse_azure(config):
    env = config.get('azure', {})
    if env is None:
        env = {}
    if len(env) != 0:
        env = parse_variables(env)
    return env


def is_string_dockerfile_envvar(string):
    if string.startswith('${') and string.endswith('}'):
        truncated_string = string.replace('{', '').replace('}', '').replace('$', '')
        if truncated_string.isupper():
            return True, truncated_string
    return False, None


def substitute_nested_envvar_strings(envvars, envvar_value):
    open_seq = '${'
    close_seq = '}'

    if open_seq in envvar_value and close_seq in envvar_value:
        regex = r"\${(.*?)\}"
        matches = re.findall(regex, envvar_value)
        for match in matches:
            try:
                envvar_value = envvar_value.replace(f"{open_seq}{match}{close_seq}", envvars.get(match))
            except TypeError:
                raise ConfigError(f"Could not parse {envvar_value} in service variables. Have you defined all nested environment variables above it?")
    return envvar_value


if __name__ == '__main__':
    print(parse_config('./experiment.yml'))
