import math


class AlertYellowChicken(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 1, 1)  # Set Start Date
        self.SetCash(50000)  # Set Strategy Cash
        equity = self.AddEquity("SPY", Resolution.Daily)
        equity.SetDataNormalizationMode(DataNormalizationMode.Raw)

        self.SetSecurityInitializer(
            lambda x: x.SetMarketPrice(self.GetLastKnownPrice(x))
        )

        self.Schedule.On(
            self.DateRules.MonthStart("SPY", 13),
            self.TimeRules.AfterMarketOpen("SPY", 30),
            self.TradeOptions,
        )

    def OnData(self, slice):
        pass

    def TradeOptions(self):
        if not self.Portfolio["SPY"].Invested:
            self.MarketOrder("SPY", 100)
