from email.utils import getaddresses
from enum import Enum
from abc import ABC, abstractmethod
import requests
import routes

class APIClientType(Enum):
    BlockchainCom = "blockchain.com"


class APIClient(ABC):  
    clientType = ""      
    @abstractmethod
    def getAddressInfo(self, addresses, numOfTxsToShow = 0):
        pass

class BlockchainComAPIClient(APIClient):
    def __init__(self):
        self.clientType = APIClientType.BlockchainCom   
         
    def getAddressInfo(self, addresses, numOfTxsToShow = 0):
        addresses = list(addresses)
        response = requests.get(routes.BLOCKCHAIN_COM_TX, params={"active": "|".join(addresses), "n": numOfTxsToShow})
        return response.json()

    def getNumOfTotalTx(self, addresses):
        return self.getAddressInfo(addresses)["wallet"]["n_tx"]


