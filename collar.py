import math


class AlertYellowChicken(QCAlgorithm):
    
    #Built in QuantConnect Initializer
    def Initialize(self):
        self.SetStartDate(2015, 1, 1)  # Set Start Date (here, first reliable start date available)
        self.SetCash(50000)  # Set Strategy Cash
        equity = self.AddEquity("SPY", Resolution.Daily) #Only need daily resolution, lower resolution generally slows algo down
        equity.SetDataNormalizationMode(DataNormalizationMode.Raw) #Realistic tradable pricing
        
        #Add SPY options
        option = self.AddOption('SPY')
        self.symbol = option.Symbol
        option.SetFilter(-15, 15, 20, 50) #w/in 15 strikes in either direction, between 20 and 50d expiration
        
        #Default price initializer
        self.SetSecurityInitializer(
            lambda x: x.SetMarketPrice(self.GetLastKnownPrice(x))
        )
        
        #Schedule Function on 13th day of month (opex is 3rd friday of each month)
        self.Schedule.On(
            self.DateRules.MonthStart("SPY", 13),
            self.TimeRules.AfterMarketOpen("SPY", 30),
            self.TradeOptions,
        )
    
    #Required QC function, safe to pass in this algo
    def OnData(self, slice):
        pass
    
    #Main trading function
    def TradeOptions(self):
        #Maintain 100 Shares of SPY
        if not self.Portfolio["SPY"].Invested:
            self.MarketOrder("SPY", 100)
        
        #Find which portfolio holdings are options
        option_invested = [
            x.Key for x in self.Portfolio if x.Value.Invested and x.Value.Type == SecurityType.Option]
        
        #If we do not have options, trade
        if len(option_invested) < 2:
            
            #Iterate over option chains
            for i in self.CurrentSlice.OptionChains:
                #Find SPY options
                if i.Key != self.symbol:
                    continue
                chain = i.Value
                
                #Find eligible put contracts, sort for furthest expiration in range
                #Collar: 20% OTM Put, find strike closest to 0.8*price
                put = [x for x in chain if x.Right == OptionRight.Put]
                put_contracts = sorted(sorted(put, key=lambda x: x.Expiry, reverse=True),
                                       key=lambda x: abs(x.Strike - 0.8*chain.Underlying.Price), reverse=False)
                
                #Find eligible call contracts, sort for furthest expiration in range
                #Collar: 20% OTM Call, find strike closest to 1.2*price
                call = [x for x in chain if x.Right == OptionRight.Call]
                call_contracts = sorted(sorted(call, key=lambda x: x.Expiry, reverse=True),
                                        key=lambda x: abs(x.Strike - 1.2*chain.Underlying.Price), reverse=False)
                
                #Bug catcher
                if len(put_contracts) == 0 or len(call_contracts) == 0:
                    return
                
                #Choose 1st put from sorted choices, and buy 1 contract
                self.put = put_contracts[0].Symbol
                self.Buy(self.put, 1)
                self.Log(
                    'Price = ' + str(self.Securities['SPY'].Price) + " Strike = " + str(put_contracts[0].Strike))
                
                #Choose 1st call from sorted choices, and sell 1 contract
                self.call = call_contracts[0].Symbol
                self.Sell(self.call, 1)
                self.Log(
                    'Price = ' + str(self.Securities['SPY'].Price) + " Strike = " + str(call_contracts[0].Strike))
