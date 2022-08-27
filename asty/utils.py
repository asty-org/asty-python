import subprocess

ASTY_EXECUTABLE_NAME = "asty"
ASTY_DOCKER_IMAGE = "astyorg/asty"


def _serialize_volumes(volumes: dict[str, str]):
    for k, v in volumes.items():
        yield '-v'
        yield f'{k}:{v}'


def run_with_container(volumes: dict[str, str], cmd: list[str]):
    query = [
        "docker", "run", "-it",
        *_serialize_volumes(volumes),
        ASTY_DOCKER_IMAGE,
        *cmd,
    ]
    print(f'Executing: {" ".join(query)}')
    return subprocess.run(
        query,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_with_executable(cmd: list[str]):
    return subprocess.run(
        [ASTY_EXECUTABLE_NAME, *cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
