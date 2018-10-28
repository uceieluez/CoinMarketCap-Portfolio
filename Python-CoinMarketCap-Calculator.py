import requests
import datetime


class CoinMarketCap:

    myAPIkey = 'Enter your Coinmarketcap API key here'
    mapURL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
    latestQuotesURL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    creditsUsed = 0

    def __init__(self, APIkey):
        self.myAPIkey = APIkey

    def AddCreditCount(self, getRequest):
        status = getRequest.get('status')
        creditCount = status.get('credit_count')
        self.creditsUsed = self.creditsUsed + creditCount


    def Get_JSON_Response(self, url):
        """Returns JSON response from a .get() request to a API coinmarketcap url with the API key header added.
        This method will use one call credit per 100 cryptocurrencies returned (rounded up)."""
        response = requests.get(url, headers={'X-CMC_PRO_API_KEY': self.myAPIkey}).json()
        CoinMarketCap.AddCreditCount(self, response)
        return response

    def ParseDataFrom_JSON_Response(self, url):
        """Returns the value of the 'data' dictionary returned by the Get_JSON_CMC_Response() method."""
        jsonResponse = CoinMarketCap.Get_JSON_Response(self, url)
        data = jsonResponse.get('data')
        return data

    def GetListOfCoinIdentifiers(self):
        """Returns a list containing embedded lists. Each embedded list contains the Coinmarketcap id, name, and ticker
        for a single cryptocurrency. This will use one call credit."""
        coinData = CoinMarketCap.ParseDataFrom_JSON_Response(self, self.mapURL)
        coinList = []
        for coins in coinData:
            coinID = coins.get('id')
            name = coins.get('name')
            ticker = coins.get('symbol')
            coinIdentifiers = [str(coinID), name, ticker]
            coinList.append(coinIdentifiers)
        return coinList

    def GetCoinData(self, coinID):
        """Gets all the coin data for the cryptocurrency(s) passed through the 'coinID' parameter. If being used for a
        single currency, the 'coinID' parameter can be a coinmarketcap ID or symbol (ticker). This script will only pass
        the Coinmarketcap ID. If being used for multiple currencies, the 'coinID' parameter must be one or more
        comma-seperated Coinmarketcap IDs (example: 1,2,3). This method will use one call credit per 100 cryptocurrencies
        returned (rounded up)."""
        coinData = CoinMarketCap.ParseDataFrom_JSON_Response(CoinMarketCap, self.latestQuotesURL + "?id=" + coinID)
        if coinData:
            return coinData
        return False

    def ParseCoinData(self, coinID):
        """This method will parse the Coinmarketcap ID, name, ticker, rank, price, and 24-hour percent change for each
        coin returned from the GetCoinData() method and assign the coin data into a dictionary within a list."""
        coinData = CoinMarketCap.GetCoinData(self, coinID)
        listOfCoinDicts = []
        for ID in coinData:
            coinDict = {
                'id': ID,
                'name': coinData.get(ID).get('name'),
                'ticker': coinData.get(ID).get('symbol'),
                'rank': coinData.get(ID).get('cmc_rank'),
                'price': coinData.get(ID).get('quote').get('USD').get('price'),
                'percent_change_24h': coinData.get(ID).get('quote').get('USD').get('percent_change_24h')
            }
            listOfCoinDicts.append(coinDict)
        return listOfCoinDicts


class Coin:

    coinIdentifiers = CoinMarketCap.GetListOfCoinIdentifiers(CoinMarketCap)

    def __init__(self, coin):
        self.coin = coin

    def CheckForCoin(self, coin):
        """This method will check to see if the data passed through the 'coin' parameter is equal to a coin identifier
        from the coinIdentifiers variable. The identifiers in coinIdentifiers are the name (case sensitive),
        ticker (capitalized), and Coinmarketcap ID for all listed cryptocurrencies. This method will return True if
        found, False if not."""
        for coins in self.coinIdentifiers:
            for identifiers in coins:
                if identifiers == coin:
                    return True
        return False

    def FindCoinMarketCapID(self, coin):
        """This method will run the 'coin' parameter through the CheckForCoin method first, then return the
         Coinmarketcap ID if found."""
        if Coin.CheckForCoin(self, coin):
            for coins in self.coinIdentifiers:
                if coin in coins:
                    return coins[0]
        return False

    def FindName(self, coin):
        """This method will run the 'coin' parameter through the CheckForCoin method first, then return the coin's
        name if found."""
        if Coin.CheckForCoin(self, coin):
            for coins in self.coinIdentifiers:
                if coin in coins:
                    return coins[1]
        return None

    def FindTicker(self, coin):
        """This method will run the 'coin' parameter through the CheckForCoin method first, then return the coin's
        ticker if found."""
        if Coin.CheckForCoin(self, coin):
            for coins in self.coinIdentifiers:
                if coin in coins:
                    return coins[2]
        return None


class Portfolio:

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def ReturnCoinNameWithTicker(self, input):
        """Return the name of a coin with the ticker in parenthesis."""
        name = Coin.FindName(Coin, input)
        ticker = Coin.FindTicker(Coin, input)
        return name + "(" + ticker + ")"

    def AskForQuantity(self, coin):
        """Ask for the quantity of the cryptocurrency passed through the 'coin' parameter."""
        coinName = Portfolio.ReturnCoinNameWithTicker(self, coin)
        while True:
            try:
                userInput = round(float(input("Please enter quantity of " + coinName + ": ")), 8)
                if userInput < 0:
                    negativeError = ValueError
                    raise negativeError
                break
            except ValueError:
                print("Error: Quantity must be greater than or equal to zero.")
        quantity = userInput
        return quantity

    def CreateQuantityDict(self, coin, quantity):
        """Create a dictionary containing the Coinmarketcap ID and the entered quantity for a coin."""
        coinID = Coin.FindCoinMarketCapID(Coin, coin)
        quantityDict = {'id': coinID, 'quantity': quantity}
        return quantityDict

    def AskForUserInput(self):
        """Ask user for a cryptocurrency. If the inputted cryptocurrency is found, it will ask the user for the quantity
        of that cryptocurrency. If the inputted cryptocurrency cannot be found, it will ask the user to
        try again. Pressing <Enter> will stop asking the user for coins."""
        listOfCoins = []
        while True:
            try:
                userInput = input(
                    "Please enter a cryptocurrency's name, ticker, or Coinmarketcap ID (<Enter> when done): ")
                trueCoin = Coin.CheckForCoin(Coin, userInput)
                if userInput == "":
                    break
                elif trueCoin:
                    quantity = Portfolio.AskForQuantity(self, userInput)
                    quantityDict = Portfolio.CreateQuantityDict(self, userInput, quantity)
                    listOfCoins.append(quantityDict)
                else:
                    raise ValueError
            except ValueError:
                print("Coin not found! (Note: names and tickers are case-sensitive.)")
        return listOfCoins

    def ReturnListOfIDs(self, inputList):
        """Returns a string of comma-seperated IDs (Example: '1,2,3'). The 'inputList' parameter must be a list of coin
        dictionaries returned by the AskForUserInput method. This is the proper format to pass in the 'coinID' parameter
        of the GetCoinData method in the CoinMarketCap class."""
        listOfIDs = []
        comma = ','
        for dicts in inputList:
            listOfIDs.append(dicts.get('id'))
        string = comma.join(listOfIDs)
        return string

    def AddQuantityToPortfolio(self, userInput):
        """Adds the user's inputted quantity of a cryptocurrency as a new dictionary value into the coin data for a
        cryptocurrency. The 'userInput' parameter must be """
        stringOfIDs = Portfolio.ReturnListOfIDs(self, userInput)
        userCoinData = CoinMarketCap.ParseCoinData(CoinMarketCap, stringOfIDs)
        for coin in userCoinData:
            for inputtedCoins in userInput:
                inputtedCoinID = inputtedCoins.get('id')
                quantity = inputtedCoins.get('quantity')
                if inputtedCoinID == coin.get('id'):
                    coin['quantity'] = quantity
        return userCoinData


class Calculator:

    def __init__(self, calculator):
        self.calculator = calculator

    def OneCoinValue(self, coinDict):
        """Returns the total value of a single cryptocurrency. The 'coinDict' parameter must be a dictionary returned
        by the ParseCoinData method in the CoinMarketCap class."""
        price = coinDict.get('price')
        quantity = coinDict.get('quantity')
        coinValue = price * quantity
        return coinValue

    def TotalCoinValue(self, listOfCoinDicts):
        """Returns the total value of all the coins in a user's portfolio. The 'listOfCoinDicts' parameter must be a
        list of dictionaries returned by the AddQuantityToPortfolio method in the Portfolio class."""
        totalValue = 0
        for coinDicts in listOfCoinDicts:
            coinValue = Calculator.OneCoinValue(self, coinDicts)
            totalValue = totalValue + coinValue
        return format(totalValue, ',.2f')


def PrintCoinData(coin):
    """Prints all coin information for a single cryptocurrency. The 'coin' parameter must be a dictionary within a list
    returned by the AddQuantityToPortfolio method in the Portfolio class."""
    name = coin.get('name')
    ticker = coin.get('ticker')
    rank = coin.get('rank')
    price = coin.get('price')
    percentChange24H = round(float(coin.get('percent_change_24h')), 2)
    if percentChange24H < 0:
        percentChange24H = str(percentChange24H) + "%"
    else:
        percentChange24H = "+" + str(percentChange24H) + "%"
    quantity = coin.get('quantity')
    value = Calculator.OneCoinValue(Calculator, coin)
    print(
        name + "(" + ticker + "):\n",
        "Rank: " + str(rank) + "\n",
        "Price: $" + format(price, ',.2f') + " (" + percentChange24H + ")\n",
        "Quantity: " + format(quantity, ',.8f') + "\n",
        "Value: $" + format(value, ',.2f'),
        "\n")


def main():
    userInput = Portfolio.AskForUserInput(Portfolio)
    portfolio = Portfolio.AddQuantityToPortfolio(Portfolio, userInput)
    totalValue = Calculator.TotalCoinValue(Calculator, portfolio)
    print("\nMY PORTFOLIO SUMMARY:\n")
    for coins in portfolio:
        PrintCoinData(coins)
    print("Total value: $" + totalValue, '\n')
    print("Total credits used: ", CoinMarketCap.creditsUsed)
    print("Last updated " + str(datetime.datetime.now()))

main()