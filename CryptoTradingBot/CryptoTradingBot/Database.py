import numpy as np
import pandas as pd
import sqlalchemy
import asyncio
from binance import AsyncClient, BinanceSocketManager
import os
import sqlite3
import time

#Delete old database
if os.path.exists('stream.db'):
    os.remove('stream.db') 

#Global variable
StrategyTimePeriod = 3600



def DatabaseShortening(engine):
    sqliteConnection = sqlite3.connect('stream.db')
    cursor = sqliteConnection.cursor()
    df = pd.read_sql('BTCUSDT', engine)
    DateTime = df.iloc[0].DateTime
    cursor.execute('DELETE FROM BTCUSDT WHERE DateTime == ?', (str(DateTime),))
    sqliteConnection.commit()
    sqliteConnection.close()
    
def createframe(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:,['s','E','p']]
    df.columns = ['symbol','DateTime','Price']
    df.Price = df.Price.astype(float)
    return df

async def main():
    engine = sqlalchemy.create_engine('sqlite:///stream.db')
    client = await AsyncClient.create()
    socket = BinanceSocketManager(client).trade_socket('BTCUSDT')
    async with socket:
        msg = await socket.recv()
        frame = createframe(msg)
        dupecheck = frame
        for i in range(StrategyTimePeriod):
                while frame.DateTime.equals(dupecheck.DateTime):
                    msg = await socket.recv()
                    frame = createframe(msg)
                frame.to_sql('BTCUSDT', engine, if_exists='append', index=False)
                dupecheck = frame
        while True:
                while frame.DateTime.equals(dupecheck.DateTime):
                    msg = await socket.recv()
                    frame = createframe(msg)
                frame.to_sql('BTCUSDT', engine, if_exists='append', index=False)
                dupecheck = frame
                DatabaseShortening(engine)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())