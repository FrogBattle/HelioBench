from os import walk
import json

MICROSERVICES_TO_RUN = ['go-api', 'memcached']
DOCKER_COMPOSE_COMMAND = 'docker-compose up --build'
DOCKER_VOLUME_NAME = 'HelioBench'
DOCKER_COMPOSE_VOLUME_PATH = '/home/experiment'


# Lists and removes all finished files for the microservices we will run
def poll_for_finish_files():
    current_filenames = next(walk(DOCKER_COMPOSE_VOLUME_PATH), (None, None, []))[2]
    print(json.dumps({"status": "success", "filenames": current_filenames}))
    return current_filenames


if __name__ == '__main__':
    poll_for_finish_files()
