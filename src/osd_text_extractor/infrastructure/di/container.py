from dishka import make_container

from .providers import AppProvider


def create_container():
    return make_container(AppProvider())
