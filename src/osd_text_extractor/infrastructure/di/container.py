from typing import Any

from dishka import make_container

from .providers import AppProvider


def create_container() -> Any:
    return make_container(AppProvider())
