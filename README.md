# trading_sim

This TCP socket application can backtest multiple trading strategies concurrently. It runs a proxy server which exposes a clean wrapper to various financial exchanges. The proxy server audits each trading strategy and ranks them based on their performance grade, allowing the client to efficiently test and analyze multiple trading strategies simultaneously.

## Usage

Ensure you have [sqlite3](https://www.sqlite.org/download.html) installed. Then, run:

```
git trading_sim https://github.com/kyhorne/trading_sim.git
cd trading_sim
pip3 install -r requirements.txt
cd trading_sim
python3 run.py -p
python3 run.py -s
```
