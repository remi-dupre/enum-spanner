import random
import sys
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


class track_block:
    '''
    Track the time spent on the given block.

    Usage:
    >> with track_block('block name'):
    >>     do_something_here()
    '''
    def __init__(self, name: str):
        self.name = name
        self.time_begin = None
        self.time_end = None

        if self.name not in TRACKING:
            TRACKING[self.name] = {'calls': 0, 'time': 0}

    def __enter__(self):
        self.time_begin = time.time()

    def __exit__(self, _type, value, traceback):
        self.time_end = time.time()
        TRACKING[self.name]['calls'] += 1
        TRACKING[self.name]['time'] += self.time_end - self.time_begin


def track(function):
    '''
    Track time spent in a decorated function or generator.
    '''
    def wrapper(*args, **kwargs):
        name = function.__qualname__

        with track_block(name):
            ret = function(*args, **kwargs)

        if not isinstance(ret, types.GeneratorType):
            return ret

        # If the function produced a generator, track all accesses to this
        # generator
        def generator_wrapper():
            try:
                while True:
                    with track_block(name):
                        val = next(ret)
                    yield val
            except StopIteration:
                pass

        return generator_wrapper()

    return wrapper


def print_tracking():
    for function, logs in sorted(TRACKING.items(), key=lambda x: -x[1]['time']):
        print(f'{function}:', file=sys.stderr)

        for key, value in logs.items():
            print(f' - {key}: {value}', file=sys.stderr)

        print(file=sys.stderr)
