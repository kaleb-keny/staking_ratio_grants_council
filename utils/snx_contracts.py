import time
import requests
import sys
from utils.utility import get_w3

class SnxContracts():

    def __init__(self,conf):
            
        self.conf    = conf
        self.setup_address_resolver()
                               
    def get_abi(self,address,chain):        
        runTime      = time.time()
        headers      = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        while True:
            try:
                return requests.get(self.conf["etherscan"][chain].format(address),headers=headers).json()["result"]
            except KeyboardInterrupt:
                return None
            except:
                self.logger.exception('issue seen with fetching abi, trying again')
                time.sleep(2)
                #in case it keeps running for more than 3 min
                #to fetch an abi, backoff and exit
                if time.time() - runTime > 180:
                    time.sleep(60)
                    self.log('abi fetch retry cound exceeded, exiting',True)
                    sys.exit(1)

    def setup_address_resolver(self):
        self.addressResolverContract = dict()
        for chain, address in self.conf["proxyAddressResolver"].items():
            w3 = get_w3(self.conf,chain)
            abi = self.get_abi(address=address,
                               chain=chain)
            contract                = w3.eth.contract(address=address,abi=abi)
            addressResolverAddress  = contract .functions.target().call()
            abi                     = self.get_abi(address=addressResolverAddress , chain=chain)
            self.addressResolverContract[chain] = w3.eth.contract(address=addressResolverAddress,
                                                                  abi=abi)
    def get_address(self,contractName,chain):
        w3 = get_w3(conf=self.conf,chain=chain)
        return self.addressResolverContract[chain].functions.getAddress(w3.toHex(text=contractName)).call()
                
    def get_snx_contract(self,contractName,chain):
        w3      = get_w3(conf=self.conf,chain=chain)
        address = self.get_address(contractName=contractName,chain=chain)
        abi     = self.get_abi(address=address,chain=chain)
        return w3.eth.contract(address=address,abi=abi)