import time
import random
import csv

import config
import requests
import json

class LatencyTest():

    def __init__(self, access_token, account_id, num_trials, keep_alive, compress):
        print ('keep alive ' + str(keep_alive))
        print ('compress ' + str(compress))

        # clear the file
        self.filename = 'REST_LATENCY' + keep_alive*'-keep-alive' + compress*'-compress' + '-' + str(num_trials) + '-trials' +'.csv'

        self.instruments = []
        self.account_id = account_id
        self.num_trials = num_trials

        self.api_url = 'https://api-fxpractice.oanda.com/'
        self.oanda_client = requests.Session()

        # requests sets connection and compressed encoding by default
        if not keep_alive:
            self.oanda_client.headers["Connection"] = "close"
        if not compress:
            self.oanda_client.headers['Accept-Encoding'] = 'identity'

        #personal token authentication
        self.oanda_client.headers['Authorization'] = 'Bearer ' + access_token

    def run_tests(self):
        with open(self.filename, 'w') as csvfile:
            reportwriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
            reportwriter.writerow(["REST API Latency Test (ms)"])
            header = [
                "open order", "close trade", 
                "get 10 quotes", "get 50 quotes", "get 100 quotes", 
                "get 10 trades", "get 50 trades", "get 100 trades", "get 500 trades"
            ]
            reportwriter.writerow(header)

            timing_rows = []

            for i in range(0, self.num_trials):
                print ("Running trial %i of %i" % (i + 1, self.num_trials))
                timing_row = []
                
                # OPEN ORDER
                totaltime, open_trade_id = self.open_order_timing()
                timing_row.append(totaltime)

                # CLOSE TRADE
                totaltime = self.close_trade_timing(open_trade_id)
                timing_row.append(totaltime)

                # GET 10 quotes
                totaltime = self.get_price_timing(10)
                timing_row.append(totaltime)

                # GET 50 quotes
                totaltime = self.get_price_timing(50)
                timing_row.append(totaltime)

                # GET 100 quotes
                totaltime = self.get_price_timing(100)
                timing_row.append(totaltime)

                # GET 10 TRADES
                totaltime = self.get_trades_timing(10)
                timing_row.append(totaltime)

                # GET 50 TRADES
                totaltime = self.get_trades_timing(50)
                timing_row.append(totaltime)

                # GET 100 TRADES
                totaltime = self.get_trades_timing(100)
                timing_row.append(totaltime)

                # GET 500 TRADES
                totaltime = self.get_trades_timing(500)
                timing_row.append(totaltime)

                timing_rows.append(timing_row)

                row = ["%.1f" % req_time for req_time in timing_row]
                reportwriter.writerow(row)

        print ("Results written to %s" % self.filename)

    def close_opened_trades(self, trade_ids):
        print ("Cleaning up open trades...")
        for trade_id in trade_ids:
            self.oanda_client.delete(self.api_url + 'v1/accounts/%s/trades/%s' % (self.account_id, trade_id))

    def get_symbol_list(self, count):
        ''' Get a number of random tradeable instruments
            Used for getting prices
        '''
        # make request to get entire tradable instruments list if it is empty
        if not self.instruments:
            response = self.oanda_client.get(self.api_url + 'v1/instruments', params={"accountId" : self.account_id})
            content = json.loads(response.content)

            for instrument in content.get('instruments'):
                self.instruments.append( instrument.get('instrument') )

        random_instruments = random.sample(self.instruments, count)

        symbol_list_str = ','.join(random_instruments)

        return symbol_list_str

    def get_price_timing(self, num_instruments):
        # fetch a list of random instruments to get prices for
        symbol_list = self.get_symbol_list(num_instruments)

        # time the price get request
        start_time = time.time()
        response = self.oanda_client.get(
            self.api_url + 'v1/accounts/%s/trades' % (self.account_id), 
            params={'instruments' : symbol_list}
            )
        totaltime = ((time.time()-start_time)*1000.0)

        return totaltime

    def open_order_timing(self):
        # time to open an order for EUR_USD
        start_time = time.time()
        data = {
            'instrument' : 'EUR_USD',
            "side" : 'buy', 
            "units" : 1, 
            "type" : 'market'
        }
        response = self.oanda_client.post(self.api_url + 'v1/accounts/%s/orders' % (self.account_id), data=data)
        totaltime = ((time.time()-start_time)*1000.0)

        content = json.loads(response.content)
        trade_id = content.get('tradeOpened').get('id')

        return totaltime, trade_id

    def close_trade_timing(self, trade_id):
        # time closing a trade
        start_time = time.time()
        response = self.oanda_client.delete(self.api_url + 'v1/accounts/%s/trades/%s' % (self.account_id, trade_id))
        totaltime = ((time.time()-start_time)*1000.0)

        return totaltime

    def get_trades_timing(self, count):
        # time to get a list of open trades
        start_time = time.time()
        params = {'count': count}
        response = self.oanda_client.get(self.api_url + 'v1/accounts/%s/trades' % (self.account_id), params=params)
        totaltime = ((time.time()-start_time)*1000.0)

        return totaltime

latency_test = LatencyTest(config.ACCESS_TOKEN, config.ACCOUNT_ID, config.TRIALS, config.KEEP_ALIVE, config.COMPRESS)
latency_test.run_tests()