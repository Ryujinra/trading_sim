import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def exchange_logger(api_req):
    def wrapper(*args, **kwargs):
        logger.info(
            "Querying the {} API: {}".format(args[0].EXCHANGE_NAME, api_req.__name__)
        )
        return api_req(*args, **kwargs)

    return wrapper
