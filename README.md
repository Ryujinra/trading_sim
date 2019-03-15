# trading_sim

This TCP socket application can backtest multiple trading strategies concurrently. It runs a proxy server which exposes a clean wrapper to various financial exchanges. The trading strategies communicate with the proxy server which maintains their respective performance metrics. Upon termination of all trading strategies, the proxy server notifies the client of each strategies performance grade, allowing the client to test and analyze multiple trading strategies concurrently.

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
