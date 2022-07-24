import schedule
import time

def sync():
    # print("I'm working...", flush=True)
    # TODO: add sync logic here
    pass

schedule.every(1).seconds.do(sync)

while True:
    schedule.run_pending()
    time.sleep(1)