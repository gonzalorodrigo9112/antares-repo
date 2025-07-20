import logging

def get_logger(name):
    formatter = logging.Formatter(
        "[\033[94m%(levelname)s\033[0m] \033[92m%(asctime)s\033[0m - \033[93m%(name)s\033[0m: %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
