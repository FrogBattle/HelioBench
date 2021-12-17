from os import remove, walk
import sys

DOCKER_COMPOSE_VOLUME_PATH = '/home/experiment'


# Lists and removes all finished files for the microservices we will run
def remove_finished_volumes(services):
    current_filenames = next(walk(DOCKER_COMPOSE_VOLUME_PATH), (None, None, []))[2]
    for service in services:
        finish_file_name = f'{service}.finish'
        if finish_file_name in current_filenames:
            print(f"Deleting {service} finish file")
            remove(f'{DOCKER_COMPOSE_VOLUME_PATH}/{finish_file_name}')


if __name__ == '__main__':
    remove_finished_volumes(sys.argv)
