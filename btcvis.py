from apscheduler.schedulers.background import BackgroundScheduler
import urllib.request
import json
import time

### global vars
btcPrice = "https://api.mybitx.com/api/1/ticker?pair=XBTMYR"
myrusdRate = "https://api.fixer.io/latest?symbols=USD,MYR"
btcBalance = 0.00656085

### methods
def updateJSON(url, filename):
  request = urllib.request.urlopen(url).read().decode("utf-8")
  file = open(filename, 'w')
  file.write(request)
  file.close()

def readJSON(filename):
  file = open(filename, 'r')
  return json.load(file)

def formatTime(epochTime):
  e = int(str(epochTime)[:10])
  return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(e))

def convertToUSD(myr):
  dump = readJSON("myrusdRate.json")
  myrRate = dump["rates"]["MYR"]
  usdRate = dump["rates"]["USD"]
  rate = myrRate/usdRate
  return float(myr)/rate

def appendToFile(line, filename):
  file = open(filename, 'a')
  file.write(str(line) + '\n')
  file.close()

def renderFromHistory(filename,n):
  file = open(filename, 'r')
  lines = file.readlines()
  lineCount = len(lines)
  for i in range(20):
    print('\n')
  printHeader()
  print("showing the last {} price updates.".format(n))
  print("You have {} BTC\n".format(btcBalance))
  print("{:<20} {:<11} {:<9} {:<11}".format("Date/Time","XBT/USD","XBT/MYR","Balance"))
  for i in range(lineCount, lineCount-n, -1):
    if i >= 0:
      line = lines[i-1].rstrip('\n').split(' ')
      time = str(line[1]) + ' ' + str(line[2])
      MYRprice = float(line[3])
      usdPrice = convertToUSD(MYRprice)
      myrBalance = btcBalance * MYRprice
      symbol = ' '
      if i > 1: 
        priceDiff = MYRprice - float(lines[i-2].rstrip('\n').split(' ')[3])
        if priceDiff > 100:
          symbol = '^'
        elif priceDiff < -100:
          symbol = 'v'
      print("{:<20} {:<11} {:<9} {:<11} {}".format(time, round(usdPrice,4), MYRprice, round(myrBalance,2), symbol))

### main app cycle
def mainAppCycle():
  updateJSON(btcPrice,"btcprice.json")        # fetching BTC price
  updateJSON(myrusdRate, "myrusdRate.json")   # fetching currency rate
  dump = readJSON("btcprice.json")
  MYRprice = (float(dump["bid"]) + float(dump["ask"])) / 2
  time = formatTime(dump["timestamp"])
  
  history = str(dump["timestamp"]) + ' ' + time +' ' + str(MYRprice)
  appendToFile(history, "pricehistory.txt")
  renderFromHistory("pricehistory.txt", 30)

### aesthetics
def printHeader():
  header = ["os           :s.        s:     -oydhhhy+        ./syhhyo:   ",
            "hd           od-       -do    odo.   `:yd:    `sdo-`  .:yd+ ",
            "hd           od-       -do   -ds       `dh    yd-        +d+",
            "hd           od-       -do   -do        dd   .dh         `dh",
            "yd.          +d/       :d+   -do        dd    hd-        /do",
            "-dh/.        `hd+.   `/dh`   -do        dd    .yd+.    -odo ",
            " `/shddddh     :shdhdhs/`    .s:        oo      -oyhhhhs+.  \n"]
  for line in header:
    print(line)

### starting scheduler
if __name__ == "__main__":
  print('script started, will render on start of next minute.')
  sched = BackgroundScheduler()
  sched.start()
  printPrice = sched.add_job(func=mainAppCycle,trigger='cron',second=1)


