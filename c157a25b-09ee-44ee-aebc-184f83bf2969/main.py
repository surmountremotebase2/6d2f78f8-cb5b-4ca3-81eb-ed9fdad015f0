from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import ATR, SMA
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Define sector-specific tickers
        self.tech_tickers = ["AAPL", "MSFT"]  # Example tech firms
        self.defense_tickers = ["LMT", "RTX"]  # Example defense firms
        self.industrial_tickers = ["CAT", "DE"]  # Example industrial firms
        self.real_estate_tech_tickers = ["Z", "RDFN"]  # Example real estate tech firms
        
        # Combine all tickers for data fetching
        self.all_tickers = self.tech_tickers + self.defense_tickers + self.industrial_tickers + self.real_estate_tech_tickers
        
        # Data requests
        self.data_list = [Asset(i) for i in self.all_tickers]

    @property
    def interval(self):
        # Daily data to capture daily swings
        return "1day"

    @property
    def assets(self):
        # Assets involved in strategy
        return self.all_tickers

    @property
    def data(self):
        # Data needed for computation
        return self.data_list

    def run(self, data):
        # Initialize allocation dict
        allocation_dict = {}

        # Calculate ATR for volatility and SMA for trend for each ticker
        for ticker in self.all_tickers:
            atr = ATR(ticker, data["ohlcv"], 14)
            sma_short = SMA(ticker, data["ohlcv"], 10)  # Short-term trend
            sma_long = SMA(ticker, data["ohlcv"], 30)  # Long-term trend

            if atr and sma_short and sma_long:
                # Consider stocks with increasing short-term moving average as compared to long-term moving average
                # and use ATR to gauge volatility (assuming higher ATR indicates higher potential return at increased risk)
                if sma_short[-1] > sma_long[-1] and atr[-1] > atr[-14]:
                    allocation = 0.25  # Aggressively allocate if both conditions are met
                elif sma_short[-1] > sma_long[-1]:
                    allocation = 0.15  # Allocate moderately if only the trend is positive
                else:
                    allocation = 0.05  # Low allocation to downtrend sectors
                
                allocation_dict[ticker] = allocation
            else:
                # No allocation if data isn't sufficient
                allocation_dict[ticker] = 0
        
        # Normalize allocations (ensure they sum to <= 1)
        total_allocation = sum(allocation_dict.values())
        if total_allocation > 1:
            allocation_dict = {k: v/total_allocation for k, v in allocation_dict.items()}
        
        return TargetAllocation(allocation_dict)