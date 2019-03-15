import random
import time
import types


def random_word(size: int, alphabet: str) -> str:
    return ''.join((random.choice(alphabet) for _ in range(size)))

def bench(function, inputs: list):
    for name, document in inputs.items():
        before_init = time.time()
        generator = function(document)
        next(generator)
        after_init = time.time()

        before_enum = time.time()
        nb_extracted = 0
        try:
            while time.time() - before_enum < 5:
                next(generator)
                nb_extracted += 1
        except StopIteration:
            print(nb_extracted)
        finally:
            after_enum = time.time()

        init_time = after_init - before_init
        enum_time = after_enum - before_enum
        bandwidth = nb_extracted / enum_time
        print(f'{name}: init {init_time} seconds, bandwidth {bandwidth} '
              f'match/s over {enum_time} seconds')

TRACKING = dict()

def track(function):
    '''
    Track time spent in a decorated function.
    '''
    def wrapper(*args, **kwargs):
        time_begin = time.time()
        ret = function(*args, **kwargs)
        time_end = time.time()

        TRACKING[function.__name__]['calls'] += 1
        TRACKING[function.__name__]['time'] += time_end - time_begin

        if not isinstance(ret, types.GeneratorType):
            return ret

        def generator_wrapper():
            try:
                while True:
                    time_begin = time.time()
                    yield next(ret)
                    time_end = time.time()

                    TRACKING[function.__name__]['calls'] += 1
                    TRACKING[function.__name__]['time'] += time_end - time_begin
            except StopIteration:
                pass

        return generator_wrapper()



    TRACKING[function.__name__] = {'calls': 0, 'time': 0}
    return wrapper

def print_tracking():
    for function, logs in TRACKING.items():
        print(f'{function}: {logs}')
