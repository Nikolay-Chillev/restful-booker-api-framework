import os

import allure

from config.config import settings


def pytest_configure(config):
    """Set Allure environment info."""
    allure_dir = config.getoption("--alluredir", default=None)
    if allure_dir:
        os.makedirs(allure_dir, exist_ok=True)
        env_file = os.path.join(allure_dir, "environment.properties")
        with open(env_file, "w") as f:
            f.write(f"Base.URL={settings.BASE_URL}\n")
            f.write(f"Timeout={settings.REQUEST_TIMEOUT}\n")
            f.write(f"Python.Version=3.11+\n")
            f.write(f"Framework=Pytest + Requests\n")
