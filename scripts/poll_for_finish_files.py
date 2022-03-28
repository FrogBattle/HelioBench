from os import walk
import json

DOCKER_COMPOSE_VOLUME_PATH = '/home/experiment'


def poll_for_finish_files():
    'Polls for all finished files for the microservices we will run'
    current_filenames = next(walk(DOCKER_COMPOSE_VOLUME_PATH), (None, None, []))[2]
    print(json.dumps({"status": "success", "filenames": current_filenames}))
    return current_filenames


if __name__ == '__main__':
    poll_for_finish_files()
