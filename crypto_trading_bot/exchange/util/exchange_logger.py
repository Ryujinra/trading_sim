from .common import ExchangeAPI
from util.logger import logger


def exchange_logger(api_req):
    def wrapper(*args, **kwargs):
        if not isinstance(args[0], ExchangeAPI):
            logger.fatal(
                '{}: is not an instance of ExchangeAPI'.format(args[0]))
        else:
            logger.info('Querying the {} API: {}'.format(
                args[0].EXCHANGE_NAME, api_req.__name__))
            return api_req(*args, **kwargs)
    return wrapper
