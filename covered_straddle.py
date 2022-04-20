import math


class AlertYellowChicken(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 1, 1)  # Set Start Date
        self.SetCash(50000)  # Set Strategy Cash
        equity = self.AddEquity("SPY", Resolution.Daily)
        equity.SetDataNormalizationMode(DataNormalizationMode.Raw)

        option = self.AddOption('SPY')
        self.symbol = option.Symbol
        option.SetFilter(-5, 5, 20, 50)

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

        if len(option_invested) < 2:
            for i in self.CurrentSlice.OptionChains:
                if i.Key != self.symbol:
                    continue
                chain = i.Value

                put = [x for x in chain if x.Right == OptionRight.Put]
                put_contracts = sorted(sorted(put, key=lambda x: x.Expiry, reverse=True),
                                       key=lambda x: abs(x.Strike - chain.Underlying.Price), reverse=False)

                call = [x for x in chain if x.Right == OptionRight.Call]
                call_contracts = sorted(sorted(call, key=lambda x: x.Expiry, reverse=True),
                                        key=lambda x: abs(x.Strike - chain.Underlying.Price), reverse=False)

                if len(put_contracts) == 0 or len(call_contracts) == 0:
                    return

                self.put = put_contracts[0].Symbol
                self.Sell(self.put, 1)
                self.Log(
                    'Price = ' + str(self.Securities['SPY'].Price) + " Strike = " + str(put_contracts[0].Strike))

                self.call = call_contracts[0].Symbol
                self.Sell(self.call, 1)
                self.Log(
                    'Price = ' + str(self.Securities['SPY'].Price) + " Strike = " + str(call_contracts[0].Strike))
