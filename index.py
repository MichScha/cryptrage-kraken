import json
import requests
import time

from requests.exceptions import HTTPError
from pathlib import Path

class pairings:
    def __init__(self):
        self.url = 'https://api-pub.bitfinex.com/v2/'
        self.masterDataParameter = 'tickers?symbols=ALL'
        self.filedir = './pairings/'
        self.filedirtemp = './pairings/temp/'
        self.fileorderbooks = './pairings/orderbooks/'
        p = Path('pairings/temp')
        p.mkdir(exist_ok=True, parents=True)
        p = Path('pairings/orderbooks')
        p.mkdir(exist_ok=True, parents=True)

    def fetchMasterData(self):
        try:
            response = requests.get(self.url + self.masterDataParameter)
            response.raise_for_status()
            validPairings = []
            #print(response.content)
            jsonPairings = json.loads(response.content)
            for pair in jsonPairings:
                #print(len(pair[0]))
                if len(pair[0]) == 7:
                    #print('Correct Pairing: ' + pair[0])
                    validPairings.append(pair[0])
            with open(self.filedir + 'pairing.json', 'w') as outfile:
                json.dump(validPairings, outfile)
            print(len(validPairings))
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
            #print("HTTP error Occured")
            #print(http_err)
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
            #print("Other error occured")
            #print(err)
        #else:
            #print('Success getting pairs!')

    def splitMasterdata(self, currency):
        f = open(self.filedir + "pairing.json", "r")
        jsonPairings = json.loads(f.read())
        validPairings = []
        for pair in jsonPairings:
            if currency in pair:
                if pair[1:4] != currency:
                    validPairings.append(pair)
                    #print(pair)
        with open(self.filedir + currency + '.json', 'w') as outfile:
            json.dump(validPairings, outfile)
    def getPairings(self):
        f = open(self.filedir + "pairing.json", "r")
        return json.loads(f.read())

    def findCircuit(self, startCurrency, compareCurrency):
        f = open(self.filedir + startCurrency + '.json', "r")
        startCurrencyPairings = json.loads(f.read())
        f = open(self.filedir + compareCurrency + '.json', "r")
        compairePairings = json.loads(f.read())
        validCircuit = []
        circuits = []
        for startCurPair in startCurrencyPairings:
            for comparePair in compairePairings:
                if startCurPair[1:4] == comparePair[1:4]:
                    # [Beginn : Beginn + Length]
                    validCircuit.append(startCurPair)
                    validCircuit.append(comparePair)
                    validCircuit.append('t' + compareCurrency + startCurrency)
                    circuits.append(validCircuit)
                validCircuit = []
                    #print("Found circuits")
                    #print(startCurPair[4:7] + '->' + startCurPair[1:4] + '->' + comparePair[4:7] + '->' + startCurPair[4:7])
        with open(self.filedir + compareCurrency + startCurrency + 'Circuit.json', 'w') as outfile:
            json.dump(circuits, outfile)

    def getOrderbooks(self, startCurrency, compareCurrency):
        f = open(self.filedir + compareCurrency + startCurrency + 'Circuit.json', "r")
        circuits = json.loads(f.read())
        precision = 'P0'
        counter = 0
        for circuit in circuits:
            i = 0
            
            for pair in circuit:
                # Check if pair orderbook already fetched
                currentPair = Path(self.filedirtemp + pair + '.json')
                if not currentPair.exists():
                    try:
                        response = requests.get(self.url + '/book/' + pair + '/' + precision)
                        response.raise_for_status()
                        jsonOrderbook = json.loads(response.content)
                        #jsonOrderbookFiltered = []
                        ask = []
                        bid = []

                        for order in jsonOrderbook:
                            if order[2] > 0:
                                bid.append(order) # seller
                            else:
                                ask.append(order) # buyer

                        with open(self.filedirtemp + 'ask_' + pair + '.json', 'w') as outfile:
                            json.dump(ask, outfile)

                        with open(self.filedirtemp + 'bid_' + pair + '.json', 'w') as outfile:
                            json.dump(bid, outfile)

                        #if(i > 0):
                            # seller
                            #for order in jsonOrderbook:
                                #if order[2] > 0:
                                    #jsonOrderbookFiltered.append(order)
                        #else:
                            # buyer
                            #for order in jsonOrderbook:
                                #if order[2] < 0:
                                    #jsonOrderbookFiltered.append(order)

                        #with open(self.filedirtemp + pair + '.json', 'w') as outfile:
                            #json.dump(jsonOrderbookFiltered, outfile)
                    except HTTPError as http_err:
                        print(f'HTTP error occurred: {http_err}')  # Python 3.6
                        status_code = http_err.response.status_code
                        if status_code == 429:
                            print("Pair: " + pair)
                            #time.sleep(10)
                    except Exception as err:
                        print(f'Other error occurred: {err}')  # Python 3.6
                        #print("Other error occured")
                    #else:
                        #print('Success getting pairs!')
                i = i + 1  
            self.calculateCircuit(circuit)
            counter = counter + 1
            if counter == 20:
                print("Sleeping")
                time.sleep(25)
                counter = 0
    def calculateCircuit(self, circuit):
        startOrderbook = []
        f = open(self.filedirtemp + 'ask_' + circuit[0] + '.json', "r")
        startOrderbook = json.loads(f.read())
        tokenOrderbook = []
        f = open(self.filedirtemp + 'bid_' + circuit[1] + '.json', "r")
        tokenOrderbook = json.loads(f.read())
        compareOrderbook = []
        f = open(self.filedirtemp + 'bid_' + circuit[2] + '.json', "r")
        compareOrderbook = json.loads(f.read())
        #console.log((100 / toFixed(buyerE1[0][0])) * toFixed(sellerE2[0][0]) * toFixed(sellerE3[0][0]))
        if len(startOrderbook) > 0 and len(tokenOrderbook) > 0 and len(compareOrderbook) > 0:
            arbitrage = 100 / float(startOrderbook[0][0]) * float(tokenOrderbook[0][0]) * float(compareOrderbook[0][0])
            
            print(circuit)
            if arbitrage > 100:
                print(circuit)
                print(arbitrage)
                #["tETHUSD", "tETHBTC", "tBTCUSD"]100.01295826377294
                found = circuit
                found.append([[float(startOrderbook[0][0]),float(startOrderbook[0][2])],[float(tokenOrderbook[0][0]),float(tokenOrderbook[0][2])],[float(compareOrderbook[0][0]),float(compareOrderbook[0][2])]])
                found.append(arbitrage)
                found.append(time.time())
                with open("arbitrage.txt", "a") as myfile:
                    #myfile.write(circuit + ':' + arbitrage + '\n')
                    json.dump(found, myfile)
                    myfile.write('\n')
                with open(self.fileorderbooks + circuit[0] + '.json', 'w') as outfile:
                    json.dump(startOrderbook, outfile)
                with open(self.fileorderbooks + circuit[1] + '.json', 'w') as outfile:
                    json.dump(tokenOrderbook, outfile)
                with open(self.fileorderbooks + circuit[2] + '.json', 'w') as outfile:
                    json.dump(compareOrderbook, outfile)
    def clearTemp(self):
        [f.unlink() for f in Path(self.filedirtemp).glob("*") if f.is_file()] 

pairing = pairings()
pairing.clearTemp()
#pairing.fetchMasterData()
#print(pairing.getPairings())
#pairing.splitMasterdata('ETH')
#pairing.splitMasterdata('USD')
#pairing.splitMasterdata('EUR')
#pairing.splitMasterdata('BTC')

#pairing.findCircuit('USD', 'BTC')
#pairing.findCircuit('EUR', 'BTC')
#pairing.findCircuit('USD', 'ETH')
#pairing.findCircuit('EUR', 'ETH')


while True:
    print("USD->BTC")
    pairing.getOrderbooks('USD', 'BTC')
    pairing.clearTemp()

    print("EUR->BTC")
    pairing.getOrderbooks('EUR', 'BTC')
    pairing.clearTemp()

    print("USD->ETH")
    pairing.getOrderbooks('USD', 'ETH')
    pairing.clearTemp()

    print("EUR->ETH")
    pairing.getOrderbooks('EUR', 'ETH')
    pairing.clearTemp()