import subprocess
import sys
from typing import Set, List

import pkg_resources
import requirements
from requirements.requirement import Requirement


def get_installed_packages() -> Set[str]:
    return set([p.project_name for p in pkg_resources.working_set])


def get_missing_packages(requirements_file: str) -> List[Requirement]:
    with open(requirements_file, 'r') as fd:
        needed = [r for r in requirements.parse(fd) if r.specifier]

    installed = get_installed_packages()
    needed = [r for r in needed if pkg_resources.safe_name(r.name) not in installed]
    return needed


def install_requirements_file(requirements_file):
    return subprocess.call([sys.executable, "-m", "pip", "install", '-r', requirements_file])
