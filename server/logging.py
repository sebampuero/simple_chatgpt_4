import logging.config
import json
import pathlib


def setup_logging(root_log_level, app_log_level):
    config_file = pathlib.Path("log_config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    print(f"Running APP LOG LEVEL {app_log_level}")
    print(f"Running ROOT LOG LEVEL {root_log_level}")
    config["loggers"]["root"]["level"] = root_log_level
    config["loggers"]["ChatGPT"]["level"] = app_log_level
    logging.config.dictConfig(config)
