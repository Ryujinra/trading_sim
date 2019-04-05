# trading_sim

This TCP socket framwork can backtest trading strategies concurrently. The system uses a load balancer to instantiate multiple strategies with a server. The server exposes a uniform wrapper to various financial exchanges and audits the performance of each trading strategy; thus, allowing the client to efficiently test and analyze multiple trading strategies simultaneously. 

## Usage

Ensure you have [sqlite3](https://www.sqlite.org/download.html) installed. Then, run:

```
git clone https://github.com/kyhorne/trading_sim.git
cd trading_sim
pip3 install -r requirements.txt
cd trading_sim
python3 run.py -p
```

Then, in a new terminal window, run:
```
python3 run.py -d
```
