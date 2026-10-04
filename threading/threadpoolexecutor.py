import time
import concurrent.futures
start = time.perf_counter()
def do_something(seconds):
    print(f'Sleeping {seconds} second..')
    time.sleep(seconds)
    print(f'Done sleeping..',{seconds})
    return seconds
# with concurrent.futures.ThreadPoolExecutor() as executor:
#     results=[]
#     for _ in range(10):
#         f1= executor.submit(do_something, 1)    
#     print(f1.result())
with concurrent.futures.ThreadPoolExecutor() as executor:
    secs=[5,4,3,2,1]
    results=[executor.submit(do_something,sec) for sec in (secs)]
    for f in concurrent.futures.as_completed(results):
        print(f.result())
    # results= executor.map(do_something, secs)
    # for result in results:
    #     print("result", result)
finish= time.perf_counter()

print(f"Finished in {round(finish-start)} second(s)")