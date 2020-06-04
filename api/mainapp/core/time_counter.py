import time


def timer(f):
    def time_count(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        delta_time = time.time() - start_time
        print('Время выполнения функции {}'.format(delta_time))
        return result

    return time_count
