import yaml
import os
import logging.config

logging.config.fileConfig('logging_config.ini')
log = logging.getLogger('music')


class MusicLibConfig:
    def __init__(self):
        current_dir = os.getcwd()
        log.debug(f'Current working directory is {current_dir}')
        self._file_name = os.path.join(current_dir, 'musiclib.dev.ini')
        self._config_content = self._read()
        self._default_options = {'add_music': True, 'album_compilation': False}

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

    @property
    def add_music_indicator(self):
        return self._config_content.get('options', self._default_options).get('add_music')

    @property
    def album_compilation_indicator(self):
        return self._config_content.get('options', self._default_options).get('album_compilation')
