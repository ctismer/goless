from __future__ import print_function

import platform
import sys
import time

from goless import backends, chan, go, selecting


QUEUE_LEN = 10000
CHANSIZE_AND_NAMES = (
    (0, 'chan_sync'),
    (-1, 'chan_async'),
    (1000, 'chan_buff')
)


def bench_channel(chan_size):
    c = chan(chan_size)

    def func():
        for _ in xrange(QUEUE_LEN):
            c.send(0)
        c.close()
    count = 0

    go(func)
    start = time.clock()
    for _ in xrange(QUEUE_LEN):
        c.recv()
        count += 1
    end = time.clock()
    return end - start


def bench_channels():
    for size, name in CHANSIZE_AND_NAMES:
        took = bench_channel(size)
        write_result(name, took)


def bench_select(use_default):
    c = chan(0)
    cases = [
        selecting.scase(c, 1),
        selecting.rcase(c),
        selecting.scase(c, 1),
        selecting.rcase(c),
    ]
    if use_default:
        cases.append(selecting.dcase())

    def sender():
        while True:
            c.send(0)
            c.recv()
    go(sender)

    start = time.clock()
    for i in xrange(QUEUE_LEN):
        selecting.select(cases)
    end = time.clock()
    return end - start


def bench_selects():
    took_nodefault = bench_select(False)
    write_result('select', took_nodefault)
    took_withdefault = bench_select(True)
    write_result('select_default', took_withdefault)


WRITE_ENABLED = True


def write_result(benchname, elapsed):
    if not WRITE_ENABLED:
        return
    w = sys.stdout.write
    w(platform.python_implementation())
    w(' ')
    w(backends.current.shortname())
    w(' ')
    w(benchname)
    w(' ')
    w(('%.5f' % elapsed))
    w('\n')


def prime():
    count = 1
    if platform.python_implementation() == 'PyPy':
        count = 10
    global WRITE_ENABLED
    WRITE_ENABLED = False
    for _ in xrange(count):
        bench_channels()
        bench_selects()
    WRITE_ENABLED = True


def main():
    prime()
    bench_channels()
    bench_selects()


if __name__ == '__main__':
    main()
