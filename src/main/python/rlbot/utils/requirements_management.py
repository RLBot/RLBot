import subprocess
import sys
import warnings
from importlib import import_module
from typing import Set, List

import pkg_resources
import requirements
from pkg_resources import Requirement as PkgRequirement
from requirements.requirement import Requirement


def is_importable(req) -> bool:
    try:
        import_module(req)
        return True
    except:
        return False


# These are not pip packages, but might get specified in a requirements.txt file anyway.
# We'll recommend it because it will help the GUI detect deficiencies in the python environment
# for running that particular bot / script.
SPECIAL_REQUIREMENTS = ['tkinter']


SUPPORTED_SPECIAL_REQUIREMENTS = [req for req in SPECIAL_REQUIREMENTS if is_importable(req)]


def get_installed_packages() -> Set[str]:
    return set([p.project_name for p in pkg_resources.working_set] + SUPPORTED_SPECIAL_REQUIREMENTS)


def get_missing_packages(requirements_file: str = None, special_reqs: List[str] = []) -> List[Requirement]:
    needed = [Requirement.parse_line(sr) for sr in special_reqs]
    if requirements_file is not None:
        with open(requirements_file, 'r') as fd, warnings.catch_warnings():
            warnings.simplefilter("ignore")
            needed += [r for r in requirements.parse(fd) if r.specifier]

    installed = get_installed_packages()
    needed = [r for r in needed if pkg_resources.safe_name(r.name) not in installed]
    return needed


def install_requirements_file(requirements_file):
    return subprocess.call([sys.executable, "-m", "pip", "install", '-r', requirements_file])


def get_packages_needing_upgrade(requirements_file: str) -> List[Requirement]:
    with open(requirements_file, 'r') as fd, warnings.catch_warnings():
        warnings.simplefilter("ignore")
        needed = [r for r in requirements.parse(fd) if r.specifier]

    pkg_resource_map = {p.project_name: p for p in pkg_resources.working_set}
    needs_upgrade = []
    for r in needed:
        safe_name = pkg_resources.safe_name(r.name)
        if safe_name in pkg_resource_map:
            existing = pkg_resource_map[safe_name]
            requirement = PkgRequirement.parse(r.line)
            if existing.version not in requirement.specifier:
                needs_upgrade.append(r)

    return needs_upgrade
