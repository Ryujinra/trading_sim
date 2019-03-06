from util.logger import logger


def exchange_logger(api_req):
    def wrapper(*args, **kwargs):
        if not args:
            logger.fatal('Failed to wrap ExchangeAPI')
        else:
            logger.info('Querying the {} API: {}'.format(
                args[0].EXCHANGE_NAME, api_req.__name__))
            return api_req(*args, **kwargs)
    return wrapper
