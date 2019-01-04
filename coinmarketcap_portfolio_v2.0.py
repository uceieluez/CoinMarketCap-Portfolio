import requests
import datetime


class CoinMarketCap(object):

    def __init__(self, my_API_Key):
        self.my_API_Key = my_API_Key
        self.mapURL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
        self.latestQuotesURL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        self.creditsUsed = 0

    def addCreditCount(self, getRequest):
        status = getRequest.get('status')
        creditCount = status.get('credit_count')
        self.creditsUsed = self.creditsUsed + creditCount

    def get_JSON_Response(self, url):
        response = requests.get(url, headers={'X-CMC_PRO_API_KEY': self.my_API_Key}).json()
        CoinMarketCap.addCreditCount(self, response)
        return response

    def parse_JSON_Response(self, url):
        jsonResponse = CoinMarketCap.get_JSON_Response(self, url)
        data = jsonResponse.get('data')
        return data

    def getCoinIdentifierList(self):
        coinData = CoinMarketCap.parse_JSON_Response(self, self.mapURL)
        coinList = []
        for coins in coinData:
            coinID = coins.get('id')
            name = coins.get('name')
            slug = coins.get('slug')
            ticker = coins.get('symbol')
            lowercaseTicker = ticker.lower()
            coinIdentifiers = [str(coinID), name, slug, ticker, lowercaseTicker]
            coinList.append(coinIdentifiers)
        return coinList

    def getCoinData(self, coinID):
        coinData = CoinMarketCap.parse_JSON_Response(self, self.latestQuotesURL + '?id=' + coinID)
        if coinData:
            return coinData
        return False

    def parseCoinData(self, coinID):
        coinData = CoinMarketCap.getCoinData(self, coinID)
        listOfCoinDicts = []
        for ID in coinData:
            coinDict = {
                'id': str(ID),
                'name': coinData.get(ID).get('name'),
                'ticker': coinData.get(ID).get('symbol'),
                'rank': str(coinData.get(ID).get('cmc_rank')),
                'price': coinData.get(ID).get('quote').get('USD').get('price'),
                'percent_change_24h': coinData.get(ID).get('quote').get('USD').get('percent_change_24h')
            }
            listOfCoinDicts.append(coinDict)
        return listOfCoinDicts


class User(object):

    def __init__(self, username, user_api_key):
        self.name = username
        self.user_api_key = user_api_key
        self.coinMarketCap = CoinMarketCap(user_api_key)
        self.coinList = self.coinMarketCap.getCoinIdentifierList()

    def verifyCoins(self, userCoins):
        userCryptocurrency = []
        for allCoins in self.coinList:
            for coins in userCoins:
                if coins.get('coin') in allCoins:
                    coins.update({'id': allCoins[0]})
                    userCryptocurrency.append(coins)
        return userCryptocurrency

    def parseUserCoinIDs(self, userCoins):
        listOfIDs = []
        comma = ','
        for coins in userCoins:
            listOfIDs.append(coins.get('id'))
        string = comma.join(listOfIDs)
        return string

    def addQuantity(self, userCoins, coinMarketCapData):
        for coinData in coinMarketCapData:
            for coins in userCoins:
                if coins.get('id') == coinData.get('id'):
                    coinData.update({'quantity': coins.get('quantity')})
        return coinMarketCapData

    def getUserCoinData(self, userCoins):
        verifiedCoins = User.verifyCoins(self, userCoins)
        userCoinIDs = User.parseUserCoinIDs(self, verifiedCoins)
        coinMarketCapData = self.coinMarketCap.parseCoinData(userCoinIDs)
        allData = User.addQuantity(self, verifiedCoins, coinMarketCapData)
        return allData


class Portfolio:

    def __init__(self, user, cryptocurrency):
        self.user = user
        self.username = user.name
        self.cryptocurrency = cryptocurrency

    def printHeader(self):
        if len(self.username) == 0 or not type(str):
            print("\nWelcome back!\n")
            print("CRYPTOCURRENCY SUMMARY:\n")
        else:
            print("\nWelcome back, " + self.username + "!\n")
            print("YOUR CRYPTOCURRENCY SUMMARY:\n")

    def printCoinName(self, coin):
        name = coin.get('name')
        ticker = coin.get('ticker')
        print(name + " (" + ticker + "):")

    def printCoinMarketCapID(self, coin):
        coinID = coin.get('id')
        print("CoinMarketCap ID: " + coinID)

    def printPrice(self, coin):
        price = format(coin.get('price'), ',.2f')
        percentChange24H = coin.get('percent_change_24h')
        if percentChange24H < 0:
            percentChange24H = str(format(percentChange24H, '.2f')) + "%"
        else:
            percentChange24H = "+" + str(format(percentChange24H, '.2f')) + "%"
        print("Price: $" + price + " (" + percentChange24H + ")")

    def printQuantity(self, coin):
        quantity = coin.get('quantity')
        if quantity < 0:
            quantity = "0.00000000"
        quantity = str(format(quantity, '.8f'))
        print("Quantity: " + quantity)

    def printCoinValue(self, coin):
        price = round(coin.get('price'), 2)
        userQuantity = coin.get('quantity')
        if userQuantity < 0:
            userQuantity = 0
        else:
            userQuantity = round(float(userQuantity), 8)
        total = format(round(price * userQuantity, 2), ',.2f')
        print("Your value: $" + str(total) + '\n')

    def printTotalValue(self, userCoins):
        totalValue = 0
        for coins in userCoins:
            price = coins.get('price')
            quantity = coins.get('quantity')
            value = price * quantity
            totalValue = totalValue + value
        formattedValue = str(format(round(totalValue, 2), ',.2f'))
        print("Total value: $" + formattedValue + '\n')

    def printFooter(self):
        print("Credits used: " + str(self.user.coinMarketCap.creditsUsed))
        print("Last update: " + str(datetime.datetime.now()))

    def printSummary(self):
        userCoinData = self.user.getUserCoinData(self.cryptocurrency)
        self.printHeader()
        for coins in userCoinData:
            self.printCoinName(coins)
            self.printCoinMarketCapID(coins)
            self.printPrice(coins)
            self.printQuantity(coins)
            self.printCoinValue(coins)
        self.printTotalValue(userCoinData)
        self.printFooter()


def main():
    me = User('Your Name', 'Your CoinMarketCap API Key')
    myCryptocurrency = [                                # POSSIBLE COIN ENTRIES:
        {'coin': 'Bitcoin', 'quantity': 0.00273573},    # Name
        {'coin': 'ethereum', 'quantity': 1.05789152},   # Lowercase Name (Slug)
        {'coin': 'LTC', 'quantity': 2.17125010},        # Ticker (Symbol)
        {'coin': 'xrp', 'quantity': 45.74663000},       # Lowercase Ticker
        {'coin': '328', 'quantity': 0.40776000}         # CoinMarketCap ID
    ]
    myPortfolio = Portfolio(me, myCryptocurrency)
    myPortfolio.printSummary()

main()
