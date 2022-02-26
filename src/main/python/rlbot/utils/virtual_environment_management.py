import os
import sys
from pathlib import Path
from subprocess import run
from types import SimpleNamespace
from typing import List
from venv import EnvBuilder

from rlbot.parsing.bot_config_bundle import RunnableConfigBundle


class EnvBuilderWithRequirements(EnvBuilder):

    def __init__(self, bundle: RunnableConfigBundle, do_post_setup: bool=True):
        # Install pip by default and add RLBot's already installed packages as a base set of dependencies
        # Allows bots with requirements like "rlbot" to not have to reinstall the rlbot package
        # Also allows bots to pin to specific versions of a package, even if a different version is installed in rlbot
        super().__init__(system_site_packages=True, with_pip=True) 
        self.bundle = bundle
        self.do_post_setup = do_post_setup

    def create(self, env_dir):
        """
        Create a virtual environment in a directory.
        Changed so system site packages is configured before post_setup is ran.

        :param env_dir: The target directory to create an environment in.
        """

        env_dir = os.path.abspath(env_dir)
        context = self.ensure_directories(env_dir)
        # See issue 24875. We need system_site_packages to be False
        # until after pip is installed.
        true_system_site_packages = self.system_site_packages
        self.system_site_packages = False
        self.create_configuration(context)
        self.setup_python(context)
        if self.with_pip:
            self._setup_pip(context)
        if not self.upgrade:
            self.setup_scripts(context)
        if true_system_site_packages:
            # We had set it to False before, now
            # restore it and rewrite the configuration
            self.system_site_packages = True
            self.create_configuration(context)
        if not self.upgrade:
            self.post_setup(context)

    def post_setup(self, context: SimpleNamespace) -> None:
        if not self.do_post_setup:
            sys.stderr.write('skipping requirements check...\n')
            return
        requirements = self.bundle.requirements_file
        if not requirements:
            raise ValueError(f'Requirements file was not specified in {self.bundle.config_path}!')
        elif not Path(requirements).exists():
            raise ValueError(f'Requirements file {requirements} was not found!')
        sys.stderr.write(f'Installing {requirements}...\n')
        sys.stderr.flush()

        # Make sure pip is installed
        args = [context.env_exe, '-m', 'ensurepip']
        finished_process = self.run_and_dump(args, timeout=120)

        # Actually update pip
        args = [context.env_exe, '-m', 'pip', 'install', '-U', 'pip']
        finished_process = self.run_and_dump(args, timeout=300)

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
