from copy import deepcopy
import json

from iterators.iterator import ISettingIterator
from iterables.iterable import ISettingIterable
from api.client import IRequestClient


class LocalSettings:
    _settings: dict[str, str] = {}

    def __init__(self, request_client: IRequestClient) -> None:
        self.request_client: IRequestClient = request_client

    def update(self, settings: dict[str, str]) -> None:

        self.update_local()
        settings_before_update = deepcopy(self._settings)

        self._settings.update(settings)

        if settings_before_update == self._settings:
            return

        self.update_remote()

    def update_remote(self) -> None:
        self.request_client.patch(self._settings)

    def update_local(self) -> None:
        response = self.request_client.get()
        self._settings.update(json.loads(response.text))


class SettingsBuffer:
    def __init__(self, *iterators: list[ISettingIterator]) -> None:
        self._iterators: list[ISettingIterator] = iterators

    def add_data_to_settings(self, settings: dict[str, str],
                             data: dict[str, str]) -> dict[str, str]:
        for key, value in data.items():
            if not key in settings:
                settings.update(data)
            else:
                settings[key].update(value)
        return settings

    def get_updated_buffer(self) -> dict[str, str]:
        settings: dict[str, str] = {}

        for iterator in self._iterators:

            request_data = iterator.iterable.get_request_data(next(iterator))
            settings = self.add_data_to_settings(settings, request_data)

        return settings
