import os
import platform
import sys
from pathlib import Path
from subprocess import run
from types import SimpleNamespace
import types
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

    def ensure_directories(self, env_dir):
        """
        Create the directories for the environment.

        Returns a context object which holds paths in the environment,
        for use by subsequent logic.
        """

        if sys.version_info == (3, 7):
            return super().ensure_directories(env_dir)

        def create_if_needed(d):
            if not os.path.exists(d):
                os.makedirs(d)
            elif os.path.islink(d) or os.path.isfile(d):
                raise ValueError('Unable to create directory %r' % d)

        if os.pathsep in os.fspath(env_dir):
            raise ValueError(f'Refusing to create a venv in {env_dir} because '
                             f'it contains the PATH separator {os.pathsep}.')
        if os.path.exists(env_dir) and self.clear:
            self.clear_directory(env_dir)
        context = types.SimpleNamespace()
        context.env_dir = env_dir
        context.env_name = os.path.split(env_dir)[1]
        prompt = self.prompt if self.prompt is not None else context.env_name
        context.prompt = '(%s) ' % prompt
        create_if_needed(env_dir)
        executable = sys._base_executable
        if not executable:  # see gh-96861
            raise ValueError('Unable to determine path to the running '
                            'Python interpreter. Provide an explicit path or '
                            'check that your PATH environment variable is '
                            'correctly set.')
        dirname, exename = os.path.split(os.path.abspath(executable))

        binpath = self._venv_path(env_dir, 'scripts')
        context.env_exe = os.path.join(binpath, exename)
        is_current_version = True

        if not os.path.exists(context.env_exe):
            exename_old = 'python.exe' if platform.system() == "Windows" else 'python3'
            env_exe = os.path.join(binpath, exename_old)
            if os.path.exists(env_exe):
                is_current_version = False
                exename = exename_old
                context.env_exe = env_exe
        context.python_exe = exename

        if is_current_version:
            context.executable = executable
            context.python_dir = dirname

            incpath = self._venv_path(env_dir, 'include')
            libpath = self._venv_path(env_dir, 'purelib')
            context.inc_path = incpath
            create_if_needed(incpath)
            create_if_needed(libpath)
            # Issue 21197: create lib64 as a symlink to lib on 64-bit non-OS X POSIX
            if ((sys.maxsize > 2**32) and (os.name == 'posix') and
                (sys.platform != 'darwin')):
                link_path = os.path.join(env_dir, 'lib64')
                if not os.path.exists(link_path):   # Issue #21643
                    os.symlink('lib', link_path)
            context.bin_path = binpath
            context.bin_name = os.path.relpath(binpath, env_dir)
            create_if_needed(binpath)

        # Assign and update the command to use when launching the newly created
        # environment, in case it isn't simply the executable script (e.g. bpo-45337)
        context.env_exec_cmd = context.env_exe
        return context

    def run_and_dump(self, args: List[str], timeout: int):
        finished_process = run(args, cwd=self.bundle.config_directory, capture_output=False, timeout=timeout)
        return finished_process


def setup_virtual_environment(runnable: RunnableConfigBundle):
    if not runnable.use_virtual_environment or not runnable.requirements_file:
        raise ValueError(f'{runnable.name} is not configured for virtual environment support!')
    builder = EnvBuilderWithRequirements(bundle=runnable)
    builder.create(Path(runnable.config_directory) / 'venv')
