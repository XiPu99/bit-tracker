from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from tkinter.messagebox import NO
from urllib.parse import parse_qs, urlparse

import requests
import routes
import json
import apiClient


class Wallet:
    numOfTx = 0
    txData = []
    def __init__(self, addr):
        self.addr = addr
        

# this is the default handler that uses Blockchain.com API 
class DefaultRequestHandler(BaseHTTPRequestHandler):

    # in-memory data structures
    # TODO: move to db
    wallets = {}
    apiClient = apiClient.BlockchainComAPIClient()

    def _set_response(self):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _set_JSON_response(self, data,statusCode = HTTPStatus.OK):
        self.send_response(statusCode)
        self.send_header('Content-type', 'application/json')
        self.end_headers()     
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))        
             
        if len(self.wallets) == 0:
            self._set_JSON_response({"message": "No wallet address found in server"})
            return
    
        if self.path.startswith(routes.GET_BALANCE):
            info = self.apiClient.getAddressInfo(self.wallets.keys())
            if info.get("wallet", None):
                self._set_JSON_response({"balance": info["wallet"]["final_balance"]})
            else:
                self._set_JSON_response(statusCode=HTTPStatus.BAD_REQUEST, data={"error": "invalid wallet address"})
        elif self.path.startswith(routes.GET_TRANSACTIONS):            
            info = self.apiClient.getAddressInfo(self.wallets.keys())
            if info.get("addresses", None) is None:
                self._set_JSON_response(statusCode=HTTPStatus.BAD_REQUEST, data={"error": "invalid wallet address"})
            self.syncWalletTxs(info)
            txs = {}
            for key,value in self.wallets.items():
                txs[key] = value.txData
            self._set_JSON_response({"txs": txs})
        else:
            self.send_error(HTTPStatus.BAD_REQUEST, message="Unsupported route")
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        if self.path.startswith(routes.POST_ADD_ADDRESS): # handle routes.POST_ADD_ADDRESS
            addrs = json.loads(post_data.decode('utf-8'))["address"]
            for addr in addrs:
                logging.info("Adding wallet with address %s", addr)
                if self.wallets.get(addr, None) is None:
                    self.wallets[addr] = Wallet(addr=addr)
                else:
                    self._set_JSON_response(statusCode=HTTPStatus.BAD_REQUEST, data={"error": f"wallet with address {addr} already exists"})
                    return
            self._set_JSON_response(data={"message": "adding wallet completes"})
        elif self.path.startswith(routes.POST_DELETE_ADDRESS): # handle routes.POST_DELETE_ADDRESS
            addrs = json.loads(post_data.decode('utf-8'))["address"]
            for addr in addrs:
                if addr in self.wallets:
                    self.wallets.pop(addr)
                else:
                    self._set_JSON_response({"error": f"wallet address {addr} does not exist"}, statusCode=HTTPStatus.BAD_REQUEST)
                    return
            self._set_JSON_response({"message": "deletion completes"})     
        elif self.path.startswith(routes.POST_SYNC): # handle routes.POST_SYNC    
            info = self.apiClient.getAddressInfo(self.wallets.keys())
            if info.get("addresses", None) is None:
                self._set_JSON_response(statusCode=HTTPStatus.BAD_REQUEST, data={"error": "invalid wallet address"})  
            self.syncWalletTxs(info=info)
            self._set_response()
        else:
            self.send_error(HTTPStatus.BAD_REQUEST)

    def syncWalletTxs(self, info):        
        for addr in info["addresses"]:
            localAddressInfo = self.wallets.get(addr["address"], None)
            walletAddr = localAddressInfo.addr
            if localAddressInfo is None:
                self.send_error(HTTPStatus.BAD_REQUEST, message="wallet address does not exist")
            elif localAddressInfo.numOfTx < addr["n_tx"]: # need to sync
                logging.info("Updating Tx data for address %s", str(walletAddr))  
                numOfNewTxsSinceLastSync = addr["n_tx"] - localAddressInfo.numOfTx
                newTxs = self.apiClient.getAddressInfo(addresses=[walletAddr], numOfTxsToShow=numOfNewTxsSinceLastSync)
                self.wallets[walletAddr].txData.append(newTxs["txs"])
                localAddressInfo.numOfTx = addr["n_tx"]
            elif localAddressInfo.numOfTx == addr["n_tx"]: # no need to sync
                logging.info("Tx data for address %s is up to date", str(walletAddr))    
            else:
                self.send_error(HTTPStatus.BAD_REQUEST)


def run(server_class=HTTPServer, handler_class=DefaultRequestHandler, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()