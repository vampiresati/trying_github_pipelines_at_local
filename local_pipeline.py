import subprocess
import sys
from pathlib import Path

import yaml


PIPELINE_FILE = Path("bitbucket-pipelines.yml")


def load_pipeline():
    if not PIPELINE_FILE.exists():
        print(f"ERROR: {PIPELINE_FILE} not found")
        sys.exit(1)

    with PIPELINE_FILE.open() as f:
        return yaml.safe_load(f)


def run_docker_command(image, command):
    docker_command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{Path.cwd()}:/workspace",
        "-w",
        "/workspace",
        image,
        "sh",
        "-c",
        command,
    ]

    print(f"\n$ {command}\n")

    result = subprocess.run(docker_command)

    return result.returncode


def run_pipeline():
    config = load_pipeline()

    image = config.get("image")

    if not image:
        print("ERROR: No Docker image specified")
        sys.exit(1)

    pipelines = config.get("pipelines", {})

    default_pipeline = pipelines.get("default")

    if not default_pipeline:
        print("ERROR: No default pipeline found")
        sys.exit(1)

    print("=" * 60)
    print("LOCAL BITBUCKET PIPELINE")
    print("=" * 60)

    print(f"Image: {image}")

    for step_number, step_config in enumerate(default_pipeline, start=1):

        step = step_config.get("step", {})

        step_name = step.get(
            "name",
            f"Step {step_number}"
        )

        scripts = step.get("script", [])

        print()
        print("=" * 60)
        print(f"STEP {step_number}: {step_name}")
        print("=" * 60)

        for command in scripts:

            print(f"\nExecuting: {command}")

            return_code = run_docker_command(
                image,
                command
            )

            if return_code != 0:
                print()
                print("=" * 60)
                print("PIPELINE FAILED")
                print("=" * 60)

                print(
                    f"Command failed with exit code {return_code}"
                )

                sys.exit(return_code)

    print()
    print("=" * 60)
    print("PIPELINE SUCCEEDED")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
