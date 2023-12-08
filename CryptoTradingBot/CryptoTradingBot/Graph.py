import sqlalchemy
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def Graph(i):
    engine = sqlalchemy.create_engine('sqlite:///stream.db')
    df = pd.read_sql('BTCUSDT', engine)
    xs = df['Time']
    ys = df['Price']
    ax1.clear()
    ax1.set_xlabel('Time\n\n' + 'Current price : ' + str(df.iloc[-1].Price) +
                   '\nPrice 60 prices (~60 seconds) ago : ' + str(df.iloc[-80].Price) +
                   '\nPrice percent change : ' + str('{:.5}'.format((1 - df.iloc[-80].Price / df.iloc[-1].Price)*100)))
    ax1.set_ylabel('Price/USD')
    ax1.set_title('BTCUSDT')
    ax1.plot(xs, ys)

def main():  
    ani = animation.FuncAnimation(fig, Graph, interval = 3600)
    plt.show()  

if __name__ == "__main__":
    main()