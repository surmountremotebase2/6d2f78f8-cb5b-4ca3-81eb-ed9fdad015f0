from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, SMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define a mix of tech and diversified assets for balance
        self.tech_tickers = ["AAPL", "MSFT", "GOOGL", "FB"]
        self.diversified_tickers = ["SPY", "QQQ", "VOO"]
        self.tickers = self.tech_tickers + self.diversified_tickers

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        # Use only ohlcv for simplicity in this example
        return []

    def run(self, data):
        allocation_dict = {}
        # Start with a conservative allocation
        base_allocation_tech = 0.10 # 10% in each tech stock
        base_allocation_diversified = (1 - base_allocation_tech * len(self.tech_tickers)) / len(self.diversified_tickers)

        for ticker in self.tickers:
            if ticker in self.tech_tickers:
                allocation_dict[ticker] = base_allocation_tech
            else:
                allocation_dict[ticker] = base_allocation_diversified

            # Check if tech stocks have dipped significantly (RSI below 30 is considered oversold)
            if ticker in self.tech_tickers:
                rsi_values = RSI(ticker, data["ohlcv"], 14)
                if rsi_values and rsi_values[-1] < 30:
                    log(f"{ticker} is oversold, considering aggressive rebalance.")
                    # Increase allocation for this tech stock aggressively
                    allocation_dict[ticker] += 0.15 # Additional 15% to this tech stock
                    # Decrease equally from diversified assets to maintain overall balance
                    decrement = (0.15 / len(self.diversified_tickers))
                    for d_ticker in self.diversified_tickers:
                        allocation_dict[d_ticker] = max(0, allocation_dict[d_ticker] - decrement)

        # Ensure total allocation does not exceed 100%
        total_allocation = sum(allocation_dict.values())
        if total_allocation > 1:
            overage = total_allocation - 1
            # Adjust downwards proportionally
            for ticker in allocation_dict.keys():
                allocation_dict[ticker] -= (allocation_dict[ticker] / total_allocation) * overage

        return TargetAllocation(allocation_dict)