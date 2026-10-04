import time
import multiprocessing
import concurrent.futures
start = time.perf_counter()

def do_something(seconds):
    print(f'Sleeping {seconds} second...')
    time.sleep(seconds)
    return'Done sleeping..'

if __name__ == "__main__":
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # for _ in range(10):
        #     f = executor.submit(do_something,1)
        # print(f.result())
        # finish = time.perf_counter()
        # print(f'Finished in {round(finish-start,2)} second(s)')
        results = [executor.submit(do_something,1) for _ in range(10)]
        for f in concurrent.futures.as_completed(results):
            print(f.result())
        finish = time.perf_counter()
        print(f'Finished in {round(finish-start,2)} second(s)')

# if __name__ == '__main__':
#     processes=[]
#     for _ in range(10):
#         p = multiprocessing.Process(target=do_something, args=[1.5])
#         p.start()
#         processes.append(p)
#     for process in processes:
#         process.join()
# finish = time.perf_counter()
# print(f'Finished in {round(finish-start,2)} second(s)'