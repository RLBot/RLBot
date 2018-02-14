import importlib

from agents.base_agent import BaseAgent


def import_agent(module_name):
    try:
        module = importlib.import_module(module_name)
        return module.Agent
    except Exception:
        return BaseAgent
