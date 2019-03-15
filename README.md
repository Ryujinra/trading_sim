# trading_sim

Backtest multiple trading strategies concurrently using historical data. 

This TCP socket application runs a proxy server which exposes a clean wrapper to various exchanges. Each trading strategy communicates synchronously with the proxy server to retrieve historical chart data. The trading strategies analyze the historical chart data and then reply by placing a limit order and requesting for the next iteration of chart data. The proxy server maintains the performance metrics of each trading strategy,  and upon termination of the trading strategy, send's the performance metrics to the client. The client then sorts the trading strategies based on their respective performance grade, allowing the user to analyze multiple trading strategies concurrently.

## Usage

Ensure you have [MySQL](https://www.mysql.com/downloads/) installed and have the environment variables configured to the naming conventions defined in /trading_sim/exchange/exchange_database. Then, run:

```
git trading_sim https://github.com/kyhorne/trading_sim.git
cd trading_sim
pip3 install -r requirements.txt
cd trading_sim
python3 run.py -h
```

To instantiate the proxy server, run:
```
python3 run.py -p
```

To begin the analysis of various trading strategies, run:
```
python3 run.py -s
```

To test your trading strategies: extend the ProxyAPI class and override the strategy function, as demonstrated by Strategy1 and Strategy2 in /trading_sim/run.py.
