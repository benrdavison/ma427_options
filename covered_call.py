import math


class AlertYellowChicken(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 1, 1)  # Set Start Date
        self.SetCash(50000)  # Set Strategy Cash
        equity = self.AddEquity("SPY", Resolution.Daily)
        equity.SetDataNormalizationMode(DataNormalizationMode.Raw)

        option = self.AddOption('SPY')
        self.symbol = option.Symbol
        option.SetFilter(0, +15, 20, 50)

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

        option_invested = [
            x.Key for x in self.Portfolio if x.Value.Invested and x.Value.Type == SecurityType.Option]

        if len(option_invested) < 1:
            for i in self.CurrentSlice.OptionChains:
                if i.Key != self.symbol:
                    continue
                chain = i.Value
                call = [x for x in chain if x.Right == OptionRight.Call]
                contracts = sorted(sorted(call, key=lambda x: x.Expiry, reverse=True),
                                   key=lambda x: abs(x.Strike - 1.2*chain.Underlying.Price), reverse=False)

                if len(contracts) == 0:
                    return

                self.call = contracts[0].Symbol
                self.Sell(self.call, 1)
                self.Log(
                    'Price = ' + str(self.Securities['SPY'].Price) + " Strike = " + str(contracts[0].Strike))
