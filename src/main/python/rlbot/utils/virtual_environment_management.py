import sys
from pathlib import Path
from subprocess import PIPE, Popen, run
from threading import Thread
from types import SimpleNamespace
from typing import List
from venv import EnvBuilder

from rlbot.parsing.bot_config_bundle import RunnableConfigBundle


class EnvBuilderWithRequirements(EnvBuilder):

    def __init__(self, bundle: RunnableConfigBundle):
        super().__init__(system_site_packages=True, clear=False, with_pip=False)
        self.bundle = bundle

    def post_setup(self, context: SimpleNamespace) -> None:
        requirements = self.bundle.requirements_file
        if not requirements:
            raise ValueError(f'Requirements file was not specified in {self.bundle.config_path}!')
        elif not Path(requirements).exists():
            raise ValueError(f'Requirements file {requirements} was not found!')
        sys.stderr.write(f'Installing {requirements}...\n')
        sys.stderr.flush()

        args = [context.env_exe, '-m', 'ensurepip']
        finished_process = self.run_and_dump(args, timeout=120)

        # Install in the virtual environment
        args = [context.env_exe, '-m', 'pip', 'install', '-U', '-r', requirements]
        finished_process = self.run_and_dump(args, timeout=300)

        if finished_process.returncode > 0:
            sys.stderr.write('FAILED to install requirements!')
            return
        sys.stderr.write('done.\n')

    def run_and_dump(self, args: List[str], timeout: int):
        finished_process = run(args, cwd=self.bundle.config_directory, capture_output=False, timeout=timeout)
        return finished_process


def setup_virtual_environment(runnable: RunnableConfigBundle):
    if not runnable.use_virtual_environment or not runnable.requirements_file:
        raise ValueError(f'{runnable.name} is not configured for virtual environment support!')
    builder = EnvBuilderWithRequirements(bundle=runnable)
    builder.create(Path(runnable.config_directory) / 'venv')

