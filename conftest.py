import platform

import pytest
from dotenv import load_dotenv

load_dotenv()


def pytest_collection_modifyitems(items):
    if platform.system() != "Windows":
        skip_gui = pytest.mark.skip(reason="GUI tests require Windows with mstsc.exe")
        for item in items:
            if "gui" in item.keywords:
                item.add_marker(skip_gui)
