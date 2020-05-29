import json
import requests
import time

from requests.exceptions import HTTPError
from pathlib import Path

class pairings:
    def __init__(self):
        self.url = 'https://api.kraken.com/0/public/'
        self.masterDataParameter = 'AssetPairs'
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
            #print(response.content)
            jsonPairings = json.loads(response.content)
            jsonPairings2 = jsonPairings["result"]
            pairingJson = {}
            for (k, v) in jsonPairings2.items():
                #print(k)
                if '.d' not in k:
                    #print(v['altname'])
                    pairingObject = {
                        k: v
                    }
                    #print(pairingObject)
                    pairingJson.update(pairingObject)
            with open(self.filedir + 'pairing.json', 'w') as outfile:
                json.dump(pairingJson, outfile)
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
        validPairings = {}
        #print(jsonPairings)
        for (k, v) in jsonPairings.items():
            #print(k)
            #print(v)
            if currency in v['altname']:
                if v['altname'][0:3] != currency:
                    pairingObject = {
                        k: v
                    }
                    validPairings.update(pairingObject)
                    #print(pair)
        with open(self.filedir + currency + '.json', 'w') as outfile:
            json.dump(validPairings, outfile)
    def getPairings(self):
        f = open(self.filedir + "pairing.json", "r")
        return json.loads(f.read())
#Start USD ->XBT
    def findCircuit(self, startCurrency, compareCurrency):
        f = open(self.filedir + startCurrency + '.json', "r")
        startCurrencyPairings = json.loads(f.read())
        f = open(self.filedir + compareCurrency + '.json', "r")
        compairePairings = json.loads(f.read())
        validCircuit = {}
        circuits = []
        for (k, v) in startCurrencyPairings.items():
            for (l, w) in compairePairings.items():
                if v['altname'][0:3] == w['altname'][0:3]:
                    # [Beginn : Beginn + Length]
                    pairingObject = {k: v}
                    validCircuit.update(pairingObject)
                    pairingObject = {l: w}
                    validCircuit.update(pairingObject)
                    pairingObject = {('X' + compareCurrency + 'Z' + startCurrency): {}}
                    validCircuit.update(pairingObject)
                    circuits.append(validCircuit)
                validCircuit = {}
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
            for (k, v) in circuit.items():
                # Check if pair orderbook already fetched
                currentPair = Path(self.filedirtemp + k + '.json')
                if not currentPair.exists():
                    try:
                        response = requests.get(self.url + 'Depth?pair=' + k)
                        response.raise_for_status()
                        jsonOrderbook = json.loads(response.content)
                        counter = counter + 1
                        #print(jsonOrderbook)
                        ask = jsonOrderbook["result"][k]['asks']
                        bid = jsonOrderbook["result"][k]['bids']
                        #print(ask)

                        with open(self.filedirtemp + 'ask_' + k + '.json', 'w') as outfile:
                            json.dump(ask, outfile)
                        with open(self.filedirtemp + 'bid_' + k + '.json', 'w') as outfile:
                            json.dump(bid, outfile)
                    except HTTPError as http_err:
                        print(f'HTTP error occurred: {http_err}')  # Python 3.6
                        status_code = http_err.response.status_code
                        if status_code == 429:
                            print("Pair: " + k)
                            #time.sleep(10)
                    except Exception as err:
                        print(f'Other error occurred: {err}')  # Python 3.6
                        #print("Other error occured")
                    #else:
                        #print('Success getting pairs!')
            self.calculateCircuit(circuit)
            if counter == 15:
                print("Sleeping")
                time.sleep(45)
                counter = 0

    def calculateCircuit(self, circuit):
        startOrderbook = {}
        tokenOrderbook = {}
        compareOrderbook = {}
        circuitArray = []
        for (i, k) in enumerate(circuit.items()): 
           # print(i)
            circuitArray.append(k[0])
            if i == 0:
                f = open(self.filedirtemp + 'ask_' + k[0] + '.json', "r")
                startOrderbook = json.loads(f.read())
            elif i == 1:
                f = open(self.filedirtemp + 'bid_'+ k[0] + '.json', "r")
                tokenOrderbook = json.loads(f.read())
            else:
                f = open(self.filedirtemp + 'bid_'+ k[0] + '.json', "r")
                compareOrderbook = json.loads(f.read())
        #console.log((100 / toFixed(buyerE1[0][0])) * toFixed(sellerE2[0][0]) * toFixed(sellerE3[0][0]))
        if len(startOrderbook) > 0 and len(tokenOrderbook) > 0 and len(compareOrderbook) > 0:
            arbitrage = 100 / float(startOrderbook[0][0]) * float(tokenOrderbook[0][0]) * float(compareOrderbook[0][0])
            
            #print(circuit)
            if arbitrage > 102:
                #print(circuit)
                #print(arbitrage)
                #["tETHUSD", "tETHBTC", "tBTCUSD"]100.01295826377294

                found = circuitArray
                found.append([[float(startOrderbook[0][0]),float(startOrderbook[0][1])],[float(tokenOrderbook[0][0]),float(tokenOrderbook[0][1])],[float(compareOrderbook[0][0]),float(compareOrderbook[0][1])]])
                found.append(arbitrage)
                found.append(time.time())
                with open("arbitrage.txt", "a") as myfile:
                    #myfile.write(circuit + ':' + arbitrage + '\n')
                    json.dump(found, myfile)
                    myfile.write('\n')

                for (i, k) in enumerate(circuit.items()): 
                    if i == 0:
                        with open(self.fileorderbooks + k[0] + '.json', 'w') as outfile:
                            json.dump(startOrderbook, outfile)
                    elif i == 1:
                        with open(self.fileorderbooks + k[0] + '.json', 'w') as outfile:
                            json.dump(tokenOrderbook, outfile)
                    else:
                        with open(self.fileorderbooks + k[0] + '.json', 'w') as outfile:
                            json.dump(compareOrderbook, outfile)
    def clearTemp(self):
        [f.unlink() for f in Path(self.filedirtemp).glob("*") if f.is_file()] 

pairing = pairings()
#pairing.clearTemp()
#pairing.fetchMasterData()
#print(pairing.getPairings())
#pairing.splitMasterdata('ETH')
#pairing.splitMasterdata('USD')
#pairing.splitMasterdata('EUR')
#pairing.splitMasterdata('XBT')

#pairing.findCircuit('USD', 'XBT')
#pairing.findCircuit('EUR', 'XBT')
#pairing.findCircuit('USD', 'ETH')
#pairing.findCircuit('EUR', 'ETH')

#pairing.findCircuit('USD', 'XBT')
#pairing.getOrderbooks('USD', 'XBT')
#pairing.clearTemp()


while True:
    print("USD->XBT")
    pairing.getOrderbooks('USD', 'XBT')
    pairing.clearTemp()

    print("EUR->XBT")
    pairing.getOrderbooks('EUR', 'XBT')
    pairing.clearTemp()

    print("USD->ETH")
    pairing.getOrderbooks('USD', 'ETH')
    pairing.clearTemp()

    print("EUR->ETH")
    pairing.getOrderbooks('EUR', 'ETH')
    pairing.clearTemp()