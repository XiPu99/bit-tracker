# bit-tracker

### Dependencies & External Library
    Python 3.7.6
    Python packages:
        - requests
        - schedule

### How to run the project
Run `python server.py` first to start the server and then you can use the command shown below to interact with the server.

Use `python client.py add addr1 addr2 ...` to add wallet addresses
Use `python client.py delete addr1 addr2 ...` to delete wallet addresses
Use `python client.py gb` to get total balance for all your addresses
Use `python client.py gt` to get all transaction data for all your addresses

### Note
I made an assumption that the API I was using had no limitation in the number of transactions it can return at a time, which turned out to not be the case. 