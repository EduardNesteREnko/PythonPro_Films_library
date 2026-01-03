import datetime
import logging
import threading
import multiprocessing

def calc_lucky_tickets(start_range, end_range, name, results_container):
    count = 0
    for i in range(start_range, end_range):
        d1 = i // 100000
        d2 = (i // 10000) % 10
        d3 = (i // 1000) % 10
        d4 = (i // 100) % 10
        d5 = (i // 10) % 10
        d6 = i % 10

        if (d1 + d2 + d3) == (d4 + d5 + d6):
            count += 1

    if isinstance(results_container, list):
        results_container.append(count)
    else:
        results_container.put(count)
    logging.info(f"{name} finished. Found: {count}")


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    mid = 500000
    end = 1000000

    logging.info("Main    : Starting THREADS")
    results_threads = []

    t1 = datetime.datetime.now()
    x1 = threading.Thread(target=calc_lucky_tickets, args=(0, mid, "thread1", results_threads))
    x2 = threading.Thread(target=calc_lucky_tickets, args=(mid, end, "thread2", results_threads))

    x1.start()
    x2.start()
    x1.join()
    x2.join()
    t2 = datetime.datetime.now()

    logging.info(f"Threads Total: {sum(results_threads)}")
    logging.info(f"Threads Time: {t2 - t1}")

    logging.info("Main    : Starting PROCESSES")
    results_queue = multiprocessing.Queue()

    t3 = datetime.datetime.now()
    p1 = multiprocessing.Process(target=calc_lucky_tickets, args=(0, mid, "process1", results_queue))
    p2 = multiprocessing.Process(target=calc_lucky_tickets, args=(mid, end, "process2", results_queue))

    p1.start()
    p2.start()

    res1 = results_queue.get()
    res2 = results_queue.get()

    p1.join()
    p2.join()
    t4 = datetime.datetime.now()

    logging.info(f"Processes Total: {res1 + res2}")
    logging.info(f"Processes Time: {t4 - t3}")


