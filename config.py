import os
import pathlib
import toml


class Config:

    __config_obj = None
    __config_file_path = ''

    def __init__(self, config_file_path) -> None:

        if not os.path.exists(config_file_path):
            raise FileNotFoundError('Cannot find the config file at %s' %
                                    config_file_path)
        config = toml.load(config_file_path)
        self.__config_file_path = config_file_path
        self.__config_obj = config

    def load(self) -> dict[str, any]:
        return self.__config_obj

    def save(self):
        with open(pathlib.Path(self.__config_file_path),
                  "w+") as old_config_file:
            toml.dump(self.__config_obj, old_config_file)
