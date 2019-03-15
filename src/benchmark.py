import random
import time


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
            while time.time() - before_enum < 1:
                next(generator)
                nb_extracted += 1
        except StopIteration:
            print(nb_extracted)
        finally:
            after_enum = time.time()

        init_time = after_init - before_init
        bandwidth = nb_extracted / (after_enum - before_enum)
        print(f'{name}: init {init_time} seconds, bandwidth {bandwidth} match/s')
