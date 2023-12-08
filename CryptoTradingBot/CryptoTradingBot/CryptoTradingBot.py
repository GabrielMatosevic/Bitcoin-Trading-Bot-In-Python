#Use this for real trading:

    #Import:
    #from binance.client import Client

    #Code for making an order:
    #client = Client
    #client.create_order()

import subprocess 
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta

#Global variable
StrategyTimePeriod = 180

#Start database
databaseapi = subprocess.Popen(['python', 'Database.py'],shell=True)

#Start graph
#graph = subprocess.Popen(['python', 'Graph.py'],shell=True)

def MomentumStrategy(entry, lookback, win, loss, qty, open_position=False):
    engine = sqlalchemy.create_engine('sqlite:///stream.db')
    while True:
        while True:
            df = pd.read_sql('BTCUSDT', engine)
            lookbackperiod = df.iloc[-lookback:]
            cumret = (lookbackperiod.Price.pct_change() +1).cumprod() - 1
            if not open_position:
                if cumret[cumret.last_valid_index()] > entry:
                    order = df.iloc[-1]
                    print("\nTrade started at " + time.strftime("%d/%m/%Y %H:%M:%S"))
                    open_position = True
                    break
        if open_position:
            while True:
                df = pd.read_sql('BTCUSDT', engine)
                sincebuy = df.loc[df.DateTime > order.DateTime]
                if len(sincebuy) > 1:
                    sincebuyret = (sincebuy.Price.pct_change() +1).cumprod() - 1
                    last_entry = sincebuyret[sincebuyret.last_valid_index()]
                    if last_entry > 0.0015:
                        qty = qty * (1 + last_entry)
                        win += 1
                        print("Trade ended at " + time.strftime("%d/%m/%Y %H:%M:%S") +
                              "\nStarting price: " + str(order.Price) + " Ending price: " + str(df.iloc[-1].Price) + 
                              "\nPrice change: " + str(df.iloc[-1].Price/order.Price) + " \nWins: " + str(win) + " \nLosses: " + str(loss) +
                              "\nBTC ammount: " + str(qty))
                        open_position = False
                        break
                    elif last_entry < -0.0015:
                        qty = qty * (1 + last_entry)
                        loss += 1
                        print("Trade ended at " + time.strftime("%d/%m/%Y %H:%M:%S") +
                              "\nStarting price: " + str(order.Price) + " Ending price: " + str(df.iloc[-1].Price) + 
                              "\nPrice change: " + str(df.iloc[-1].Price/order.Price) + " \nWins: " + str(win) + " \nLosses: " + str(loss) +
                              "\nBTC ammount: " + str(qty))
                        open_position = False
                        break

def BollingerBandsMAStrategy(lookback, win, loss, qty, open_position=False):
    engine = sqlalchemy.create_engine('sqlite:///stream.db')
    while True:
        while True:
            df = pd.read_sql('BTCUSDT', engine)
            lookbackperiod = df.iloc[-(lookback*20):]
            MA = lookbackperiod['Price'].mean()
            STDEV = 2 * lookbackperiod['Price'].std()
            BOLD = MA - STDEV
            if not open_position:
                if  lookbackperiod.iloc[-1].Price < BOLD:
                    order = df.iloc[-1]
                    print("\nTrade started at " + time.strftime("%d/%m/%Y %H:%M:%S"))
                    open_position = True
                    break
        if open_position:
            while True:
                df = pd.read_sql('BTCUSDT', engine)
                sincebuy = df.loc[df.DateTime > order.DateTime]
                lookbackperiod = df.iloc[-(lookback*20):]
                MA = lookbackperiod['Price'].mean()
                STDEV = 2.5 * lookbackperiod['Price'].std()
                BOLU = MA + STDEV
                if len(sincebuy) > 1:
                    sincebuyret = (sincebuy.Price.pct_change() +1).cumprod() - 1
                    last_entry = sincebuyret[sincebuyret.last_valid_index()]
                    if last_entry > 0.0015 or sincebuy.iloc[-1].Price > BOLU:
                        qty = qty * (1 + last_entry)
                        win += 1
                        print("Trade ended at " + time.strftime("%d/%m/%Y %H:%M:%S") +
                              "\nStarting price: " + str(order.Price) + " Ending price: " + str(df.iloc[-1].Price) + 
                              "\nPrice change: " + str(df.iloc[-1].Price/order.Price) + " \nWins: " + str(win) + " \nLosses: " + str(loss) +
                              "\nBTC ammount: " + str(qty))
                        open_position = False
                        break
                    elif last_entry < -0.0015:
                        qty = qty * (1 + last_entry)
                        loss += 1
                        print("Trade ended at " + time.strftime("%d/%m/%Y %H:%M:%S") +
                              "\nStarting price: " + str(order.Price) + " Ending price: " + str(df.iloc[-1].Price) + 
                              "\nPrice change: " + str(df.iloc[-1].Price/order.Price) + " \nWins: " + str(win) + " \nLosses: " + str(loss) +
                              "\nBTC ammount: " + str(qty))
                        open_position = False
                        break

def BBsMomentumStrategy(lookback, win, loss, qty, open_position=False):
    engine = sqlalchemy.create_engine('sqlite:///stream.db')
    cutloss = qty*0.98
    while True:
        if qty < cutloss:
            print("\nTrading stopped, loss is greater than 2 percent")
            break
        while True:
            df = pd.read_sql('BTCUSDT', engine)
            lookbackperiod = df.iloc[-lookback:]
            cumret = (lookbackperiod.Price.pct_change() +1).cumprod() - 1
            BBlookbackperiod = df.iloc[-(lookback*20):]
            MA = BBlookbackperiod['Price'].mean()
            STDEV = 1.5 * BBlookbackperiod['Price'].std()
            BOLD = MA - STDEV
            entry = 0.3 * (MA / BOLD - 1)
            if not open_position:
                if  lookbackperiod.iloc[-1].Price < BOLD and cumret[cumret.last_valid_index()] > entry:
                    order = df.iloc[-1]
                    print("\nTrade started at " + time.strftime("%d/%m/%Y %H:%M:%S"))
                    open_position = True
                    break
        if open_position:
            while True:
                df = pd.read_sql('BTCUSDT', engine)
                sincebuy = df.loc[df.DateTime > order.DateTime]
                BBlookbackperiod = df.iloc[-(lookback*20):]
                MA = BBlookbackperiod['Price'].mean()
                STDEV = 2 * BBlookbackperiod['Price'].std()
                BOLU = MA + STDEV
                if len(sincebuy) > 1:
                    sincebuyret = (sincebuy.Price.pct_change() +1).cumprod() - 1
                    last_entry = sincebuyret[sincebuyret.last_valid_index()]
                    if sincebuy.iloc[-1].Price > BOLU and last_entry > 0:
                        qty = qty * (1 + last_entry)
                        win += 1
                        print("Trade ended at " + time.strftime("%d/%m/%Y %H:%M:%S") +
                                "\nStarting price: " + str(order.Price) + " Ending price: " + str(sincebuy.iloc[-1].Price) + 
                                "\nPrice change: " + str(last_entry) + " \nWins: " + str(win) + " \nLosses: " + str(loss) +
                                "\nBTC ammount: " + str(qty))
                        open_position = False
                        break
                    if -0.0015 < 1 - BOLU / order.Price:
                        stoploss = -0.0015
                    else:
                        stoploss = 1 - BOLU / order.Price
                    if last_entry < stoploss:
                        qty = qty * (1 + last_entry)
                        loss += 1
                        print("Trade ended at " + time.strftime("%d/%m/%Y %H:%M:%S") +
                                "\nStarting price: " + str(order.Price) + " Ending price: " + str(sincebuy.iloc[-1].Price) + 
                                "\nPrice change: " + str(last_entry) + " \nWins: " + str(win) + " \nLosses: " + str(loss) +
                                "\nBTC ammount: " + str(qty))
                        open_position = False
                        break

def main():
    print("Strategy will start at " + (datetime.now() + timedelta(seconds = StrategyTimePeriod*7)).strftime("%d/%m/%Y %H:%M:%S") + "\n\n")
    time.sleep(StrategyTimePeriod*7)
    print("Strategy started at " + time.strftime("%d/%m/%Y %H:%M:%S") + "\n")
    #MomentumStrategy(0.001, MomentumTimePeriod, 0, 0, 1)
    #BollingerBandsMAStrategy(BollingerBandsPeriod, 0, 0, 1)
    BBsMomentumStrategy(StrategyTimePeriod, 0, 0, 1)

if __name__ == "__main__":
    main()
