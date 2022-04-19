import yaml


class MusicLibConfig:
    def __init__(self):
        self._file_name = '/Users/manolo/Documents/python/musiclib/musiclib.dev.ini'
        self._config_content = self._read()
        pass

    def _read(self):
        with open(self._file_name) as file_handler:
            config_content = yaml.load(file_handler, Loader=yaml.FullLoader)
        return config_content

    @property
    def fm_api_key(self):
        return self._config_content.get('fm').get('API_key')

    @property
    def fm_url(self):
        return self._config_content.get('fm').get('URL')
