import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file_handler = logging.StreamHandler()
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def exchange_logger(api_req):
    def wrapper(*args, **kwargs):
        if not args:
            logger.fatal("Failed to wrap ExchangeAPI")
        else:
            logger.info(
                "Querying the {} API: {}".format(
                    args[0].EXCHANGE_NAME, api_req.__name__
                )
            )
            return api_req(*args, **kwargs)

    return wrapper
