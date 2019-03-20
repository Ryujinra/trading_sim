import pandas as pd


class Bookkeeper:
    def __init__(self):
        # Instantiate a new data frame.
        self.metric = pd.DataFrame(
            columns=["Strategy Name", "Percent Change", "Trades Made"]
        )

    def log(self):
        # Log the data frame while ignoring the index.
        print(self.metric.to_string(index=False))

    def handler(self, data):
        # Append new data to the data frame.
        self.metric = self.metric.append(
            {
                "Strategy Name": data[0],
                "Percent Change": "{:.2f}%".format(data[1]),
                "Trades Made": data[2],
            },
            ignore_index=True,
        )
