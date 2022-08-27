import subprocess

ASTY_EXECUTABLE_NAME = "asty"
ASTY_DOCKER_IMAGE = "astyorg/asty"


def _serialize_volumes(volumes: dict[str, str]):
    for k, v in volumes.items():
        yield '-v'
        yield f'{k}:{v}'


def run_with_container(cmd: list[str], volumes: dict[str, str] = None, input: str = None):
    if volumes is None:
        volumes = {}
    query = [
        "docker", "run", "-i",
        *_serialize_volumes(volumes),
        ASTY_DOCKER_IMAGE,
        *cmd,
    ]
    print(f'Executing: {" ".join(query)}')
    return subprocess.run(
        query,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        input=input,
    )


def run_with_executable(cmd: list[str]):
    return subprocess.run(
        [ASTY_EXECUTABLE_NAME, *cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
