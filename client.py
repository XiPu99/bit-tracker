import requests
import logging
import routes
import sys

DEFAULT_HOST = 'http://127.0.0.1:8080'

def main():
    if sys.argv[1] == "add":
        res = requests.post(DEFAULT_HOST+routes.POST_ADD_ADDRESS, json={"address": list(sys.argv[2:])})
        print(res.json())
    elif sys.argv[1] == "delete":
        res = requests.post(DEFAULT_HOST+routes.POST_DELETE_ADDRESS, json={"address": list(sys.argv[2:])})
        print(res.json())
    elif sys.argv[1] == "sync":
        requests.post(DEFAULT_HOST+routes.POST_SYNC)
    elif sys.argv[1] == "gt":
        response = requests.get(DEFAULT_HOST+routes.GET_TRANSACTIONS)
        print(response.json())
    elif sys.argv[1] == "gb":
        response = requests.get(DEFAULT_HOST+routes.GET_BALANCE)
        print(response.json())
    else:
        raise Exception("Unsupported operation %s", sys.argv[1])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(e)
