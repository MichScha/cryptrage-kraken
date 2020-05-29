const fetch = require('node-fetch')
const url = 'https://api-pub.bitfinex.com/v2/'

let tickerPairs = []

let initial = {
    usd: { from: "USD", to: [] },
    eur: { from: "EUR", to: [] },
    btc: { from: "BTC", to: [] },
    eth: { from: "ETH", to: [] }
}

let basicOrderBooks = {
}

let circuits = [["ETH", "X", "BTC"]]

function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
      if ((new Date().getTime() - start) > milliseconds){
        break;
      }
    }
  }

getPairs()

function test() {
    //console.log(initial.btc.to)
    initial.eth.to.forEach(element => {
        if (initial.btc.to.includes(element)) {
            //console.log("ETH --> " + element + "-->BTC")
        }
    });
    initial.usd.to.forEach(element => {
        if (initial.btc.to.includes(element)) {
            //console.log("USD --> " + element + "-->BTC")
            if(false){
               // console.log(element)

            calculate('t' + element + 'USD').then(res1 => {
                let sellerE1 = []
              console.log("t" + element + 'USD')
                console.log("res1: " + res1.length)
                res1.forEach(element => {
                    if (element[2] < 0) {
                        sellerE1.push(element)
                    }
                })
                sleep(1001);
                calculate('t' + element + 'BTC').then(res2 => {
                    
                    let buyerE2 = []
/*                     console.log("t" + element + 'BTC')
                    console.log("res2: " + res2.length) */
                    res2.forEach(element => {
                        if (element[2] > 0) {
                            buyerE2.push(element)
                        }
                    })
                    sleep(1001);
                    calculate('tBTCUSD').then(res3 => {
                        let buyerE3 = []
/*                         console.log("tBTCUSD")
                        console.log("res3: " + res3.length) */
                        res3.forEach(element => {
                            if (element[2] > 0) {
                                buyerE3.push(element)
                            }
                        })
                        
                        console.log("####### Pair: USD->" + element + "->BTC->USD #######")
                        console.log("buyerE1: " + toFixed(sellerE1[0][0]))
                        console.log("sellerE2: " + toFixed(buyerE2[0][0]))
                        console.log("sellerE3: " + toFixed(buyerE3[0][0]))
                        console.log((100 / toFixed(sellerE1[0][0])) * toFixed(buyerE2[0][0]) * toFixed(buyerE3[0][0]))
                        console.log("Fees: " + (100 * 3 * 0.002))
                        console.log("############################")
                        sleep(1001);
                    })
                        .catch(err => {
                            console.log(err)
                        })
                })
                    .catch(err => {
                        console.log(err + "ELement: " + element)
                    })
            })
                .catch(err => {
                    console.log(err + "ELement: " + element)
                })
            }
        }
        if (initial.eth.to.includes(element)) {
            //console.log("USD --> " + element + "-->ETH")
        }
    });
    initial.eur.to.forEach(element => {
        if (initial.btc.to.includes(element)) {
            //console.log("EUR --> " + element + "-->BTC")
            
            calculate('t' + element + 'EUR').then(res1 =>{
                let buyerE1 = []
                res1.forEach(element => {
                    if(element[2] > 0){
                        buyerE1.push(element)
                    }
                })
                sleep(1001);
                calculate('t' + element + 'BTC').then(res2 =>{
                    let sellerE2 = []
                    res2.forEach(element => {
                        if(element[2] < 0){
                            sellerE2.push(element)
                        }
                    })
                    sleep(1001);
                    calculate('tBTCEUR').then(res3 =>{
                        let sellerE3 = []
                        res3.forEach(element => {
                            if(element[2] < 0){
                                sellerE3.push(element)
                            }
                        })
                        console.log("####### Pair: EUR->" + element + "->BTC->EUR #######")
                        console.log("buyerE1: " + toFixed(buyerE1[0][0]))
                        console.log("sellerE2: " + toFixed(sellerE2[0][0]))
                        console.log("sellerE3: " + toFixed(sellerE3[0][0]))
                        console.log((100 / toFixed(buyerE1[0][0])) * toFixed(sellerE2[0][0]) * toFixed(sellerE3[0][0]))
                        console.log("Fees: " + (100*3*0.002))
                        console.log("############################")
                        sleep(1001);
                    })
                    .catch(err =>{
                        console.log(err)
                    })
                })
                .catch(err =>{
                    console.log(err)
                })
            })
            .catch(err =>{
                console.log(err)
            })
        }

        if (initial.eth.to.includes(element)) {
            //console.log("EUR --> " + element + "-->ETH")
            //calculate('t' + element + 'EUR', 't' + element + 'ETH', 'tETHEUR')

            /*
            calculate('t' + element + 'EUR').then(res1 =>{
                let buyerE1 = []
                res1.forEach(element => {
                    if(element[2] > 0){
                        buyerE1.push(element)
                    }
                })
                calculate('t' + element + 'ETH').then(res2 =>{
                    let sellerE2 = []
                    res2.forEach(element => {
                        if(element[2] < 0){
                            sellerE2.push(element)
                        }
                    })
                    calculate('tETHEUR').then(res3 =>{
                        let sellerE3 = []
                        res3.forEach(element => {
                            if(element[2] < 0){
                                sellerE3.push(element)
                            }
                        })
                        console.log("####### Pair: EUR->" + element + "->ETH->EUR #######")
                        console.log("buyerE1: " + buyerE1[0][0])
                        console.log("sellerE2: " + sellerE2[0][0])
                        console.log("sellerE3: " + sellerE3[0][0])
                        console.log((100 / buyerE1[0][0]) * sellerE2[0][0] * sellerE3[0][0])
                        console.log("Fees: " + (100*3*0.002))
                        console.log("############################")
                    })
                    .catch(err =>{
                        console.log(err)
                    })
                })
                .catch(err =>{
                    console.log(err)
                })
            })
            .catch(err =>{
                console.log(err)
            })*/
        }
    });
}

async function calculate(e1) {
    console.log(Object.keys(basicOrderBooks))
    if(!basicOrderBooks[''+e1+'']){
        //console.log("XXX")
        //console.log(basicOrderBooks.tBTCUSD)
        let precision = 'P0'
        let queryParams = ''
        try {
            let pathParamsE1 = 'book/' + e1 + "/" + precision
            let reqE1 = await fetch(`${url}/${pathParamsE1}`)
            let res = await reqE1.json()

            basicOrderBooks[e1] = res
            console.log("PairRequest: " + e1)
            
            return res
        }
        catch (err) {
            console.log(err)
        }
    } else {
        console.log("999999999999999999999999999999999999999999")
        return basicOrderBooks[e1]
    }


}

function findStartingCircuits() {
    tickerPairs.forEach(pair => {
        if (pair.pairing[1] == 'USD') {
            if (!pair.pairing.includes('EUR')) {
                initial.usd.to.push(pair.pairing[0])
            }
        } else if (pair.pairing[1] == 'EUR') {
            if (!pair.pairing.includes('USD')) {
                initial.eur.to.push(pair.pairing[0])
            }
        } else if (pair.pairing[1] == 'BTC') {
            initial.btc.to.push(pair.pairing[0])
        } else if (pair.pairing[1] == 'ETH') {
            initial.eth.to.push(pair.pairing[0])
        }
    });
    //console.log(initial)
}

async function getPairs() {
    //https://api-pub.bitfinex.com/v2/tickers?symbols=ALL
    try {
        let pathParams = 'tickers'
        let queryParams = 'symbols=ALL'
        let req = await fetch(`${url}/${pathParams}?${queryParams}`)
        let response = await req.json()
        // console.log(`STATUS ${req.status} - ${JSON.stringify(response)}`)
        response.forEach(element => {

            if (element[0].length == 7) {
                //console.log(element[0])
                let firstT = element[0].substring(1, 4)
                let secondT = element[0].substring(4, 7)
                let pair = {
                    //   [element[0]]: {
                    pairing: [firstT, secondT],
                    buyer: "",
                    seller: "",
                    //  }
                }
                //pair.pairing.push(element[0].substring(1, 4))
                //console.log(pair)
                tickerPairs.push(pair)
            }
        });
        findStartingCircuits()
        test()
    }
    catch (err) {
        console.log(err)
    }
}

// Ticker definitions
// https://api-pub.bitfinex.com/v2/tickers?symbols=ALL
let tickers = {
    tETHUSD: {
        pairing: ["ETH", "USD"],
        buyer: "",
        seller: "",
    },
    tVETBTC: {
        pairing: ["VET", "BTC"],
        buyer: "",
        seller: ""
    }
}

// Request current orderbooks
Object.keys(tickers).forEach(element => {
    //request(element)
    //console.log(element)
});

async function request(element) {
    let precision = 'P0'
    let queryParams = ''
    try {
        let pathParams = 'book/' + element + "/" + precision
        let req = await fetch(`${url}/${pathParams}?${queryParams}`)
        let response = await req.json()
        // console.log(`STATUS ${req.status} - ${JSON.stringify(response)}`)
        //console.log("Orderbook for: " + element)
        //console.log(response)
        //console.log(response.length)
        tickers[element].buyer = response.slice(0, 25);
        console.log(tickers[element].buyer[0][0])
        console.log(toFixed(-4.2e-12))
        tickers[element].seller = response.slice(26, 49);
    }
    catch (err) {
        console.log(err)
    }
}

// no scientific numbers in array
function toFixed(num) {
    let numStr = String(num);

    if (Math.abs(num) < 1.0) {
        let e = parseInt(num.toString().split('e-')[1]);
        if (e) {
            let negative = num < 0;
            if (negative) num *= -1
            num *= Math.pow(10, e - 1);
            numStr = '0.' + (new Array(e)).join('0') + num.toString().substring(2);
            if (negative) numStr = "-" + numStr;
        }
    }
    else {
        let e = parseInt(num.toString().split('+')[1]);
        if (e > 20) {
            e -= 20;
            num /= Math.pow(10, e);
            numStr = num.toString() + (new Array(e + 1)).join('0');
        }
    }

    return numStr;
}
