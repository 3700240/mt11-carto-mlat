import numpy as np
import pandas as pd

from datetime import timedelta

from .projection import sph2lcc

def iterate_icao24_callsign(data):
    for _, chunk in data.groupby(["icao24", "callsign"]):
        yield chunk

def iterate_time(data, threshold):
    idx = np.where(data.timestamp.diff().dt.total_seconds() > threshold)[0]
    start = 0
    for stop in idx:
        yield data.iloc[start:stop]
        start = stop
    yield data.iloc[start:]


def iterate_all(data, threshold):
    for group in iterate_icao24_callsign(data):
        yield from iterate_time(group, 20000)

class Flight:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return (
            f"Flight {self.callsign} with aircraft {self.icao24} "
            f"on {self.min('timestamp'):%Y-%m-%d} "
        )

    def __lt__(self, other):
        return self.min("timestamp") <= other.min("timestamp")

    def max(self, feature):
        return self.data[feature].max()

    def min(self, feature):
        return self.data[feature].min()

    @property
    def callsign(self):
        return self.min("callsign")

    @property
    def icao24(self):
        return self.min("icao24")

    def plot_lcc(self, ax, **kwargs):
        x, y = sph2lcc(self.data["longitude"], self.data["latitude"])
        ax.plot(x, y, **kwargs)

class FlightCollection:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"FlightCollection with {len(self)} flights"

    def summary(self):
        return pd.DataFrame.from_records(
        [
            {
                "icao24": chunk.icao24.min(),
                "callsign": chunk.callsign.min(),
                "start": chunk.timestamp.min(),
                "stop": chunk.timestamp.max(),
            }
            for chunk in iterate_all(self.data, 20000)
        ])

    @classmethod
    def read_json(cls, filename):
        return cls(pd.read_json(filename))

    def __iter__(self):
        for group in iterate_icao24_callsign(self.data):
            for elt in iterate_time(group, 20000):
                yield Flight(elt)

    def __len__(self):
        return sum(1 for _ in self)

    def __getitem__(self, key):
        if isinstance(key, str):
            result = FlightCollection(
                self.data.query("callsign == @key or icao24 == @key")
            )
        if isinstance(key, pd.Timestamp):
            before = key
            after = key + timedelta(days=1)
            result = FlightCollection(self.data.query("@before < timestamp < @after"))

        if len(result) == 1:
            return Flight(result.data)
        else:
            return result