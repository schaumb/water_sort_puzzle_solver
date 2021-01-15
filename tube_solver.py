#!/usr/bin/python3

from os import linesep
from sys import stdout, stdin
from copy import deepcopy
from itertools import zip_longest, dropwhile, groupby, islice, filterfalse, chain
from heapq import heappush, heappop
from termcolor import colored

need_msg = stdin.isatty()


def iterable_len(iterable):
    return sum(1 for elem in iterable)


def pretty_state_element(tube_element):
    switcher = {
        'e': colored('█e█', 'grey'),
        'r': colored('█r█', 'red', attrs=['dark']),
        'g': colored('█g█', 'green', attrs=['dark']),
        'l': colored('█l█', 'green'),
        'y': colored('█y█', 'yellow'),
        'b': colored('█b█', 'yellow', attrs=['dark']),
        'q': colored('█q█', 'blue'),
        'd': colored('█d█', 'blue', attrs=['dark']),
        'm': colored('█m█', 'magenta'),
        'p': colored('█p█', 'magenta', attrs=['dark']),
        'c': colored('█c█', 'cyan'),
        'o': colored('█o█', 'white'),
    }
    stdout.write("{}".format(switcher.get(tube_element, ' ' + tube_element + ' ')))


def pretty_state_line(state, line):
    if line < 4:
        for tube in state:
            stdout.write('|')
            pretty_state_element(tube[line])
        stdout.write('|')
    else:
        stdout.write(' \\_/' * len(state) + ' ')


def pretty_state(state):
    for line in range(5):
        pretty_state_line(state, line)
        stdout.write(linesep)


def pretty_states_header(nth, tube_count, priostr):
    if nth % 3 != 0:
        stdout.write('  -  ')
    stdout.write(priostr + ' ' * (tube_count * 4 + 1 - len(priostr)))
    if nth % 3 == 2:
        stdout.write(linesep)


def pretty_states(states):
    for tup in zip_longest(*([iter(states)] * 3)):
        for line in range(5):
            first = True
            for state in tup:
                if not state: break
                if first:
                    first = False
                else:
                    stdout.write('  -  ')
                pretty_state_line(state, line)
            stdout.write(linesep)
        stdout.write(linesep)


def is_empty_tube_element(tube_element):
    return tube_element == ' '


def is_empty_tube(tube):
    return is_empty_tube_element(tube[3])


def is_full_tube(tube):
    return not is_empty_tube_element(tube[0])


def fillable_empty_tube_element_indexes(tube):
    return dropwhile(lambda i: not is_empty_tube_element(tube[i]), range(3, -1, -1))


def top_tube_element_indices(tube):
    return next(iter(groupby(dropwhile(lambda i: is_empty_tube_element(tube[i]), range(4)), lambda i: tube[i])))[1]


def tube_components(tube):
    return map(lambda tup: tup[1], groupby(tube))


def not_empty_tube_components(tube):
    return islice(tube_components(tube), not is_full_tube(tube), None)


def same_top_not_empty_tube_component(tube1, tube2):
    return next(iter(next(iter(not_empty_tube_components(tube1))))) == next(
        iter(next(iter(not_empty_tube_components(tube2)))))


def can_be_fill_in(from_tube, to_tube):
    return not is_full_tube(to_tube) and (is_empty_tube(to_tube) or
                                          same_top_not_empty_tube_component(from_tube, to_tube)
                                          and iterable_len(top_tube_element_indices(from_tube)) <= iterable_len(
                fillable_empty_tube_element_indexes(to_tube))
                                          )


def tube_from_fill_indices(state):
    return filterfalse(
        lambda i: is_empty_tube(state[i]) or is_full_tube(state[i]) and iterable_len(tube_components(state[i])) == 1,
        range(len(state)))


def tube_to_fill_indices(state, filterable, i, from_is_one_component):
    return filter(lambda j:
                  i != j and
                  j not in filterable and
                  (not from_is_one_component or not is_empty_tube(state[j])) and
                  can_be_fill_in(state[i], state[j]) and
                  (not from_is_one_component or j < i or iterable_len(not_empty_tube_components(state[j])) > 1)
                  , range(len(state)))


def empty_tubes_indices(state):
    return filter(lambda i: is_empty_tube(state[i]), range(len(state)))


def next_states(state):
    nonew = set(islice(empty_tubes_indices(state), 1, None))
    for i in tube_from_fill_indices(state):
        one_component = iterable_len(not_empty_tube_components(state[i])) == 1
        for j in tube_to_fill_indices(state, nonew, i, one_component):
            cpstate = deepcopy(state)
            for from_i, to_j in zip(top_tube_element_indices(cpstate[i]),
                                    fillable_empty_tube_element_indexes(cpstate[j])):
                cpstate[i][from_i], cpstate[j][to_j] = cpstate[j][to_j], cpstate[i][from_i]
            yield cpstate, i, j, iterable_len(top_tube_element_indices(state[i]))


def solve_state(start_state, need_print=False):
    state_index = 0

    def prioritize_state(state):
        nonlocal state_index
        need_steps, big_components, empties = 0, 0, 0
        bottom_elements = set()
        for tube in state:
            if is_empty_tube(tube):
                empties += 1
                continue

            tube_comps = list(map(list, not_empty_tube_components(tube)))
            need_steps += len(tube_comps) - (tube[3] not in bottom_elements)
            big_components += sum(map(iterable_len, tube_comps)) - len(tube_comps)
            bottom_elements.add(tube[3])

        state_index += 1
        return (need_steps, -big_components, -empties, state_index), state

    if need_print:
        print("Start state:")
        pretty_state(start_state)

    heap = [prioritize_state(start_state)]
    parent = {}
    fin_prio, fin_state = None, None

    while heap:
        prio, curr_state = heappop(heap)

        if need_print:
            print("Current state:")
            print(prio)
            pretty_state(curr_state)

        if not prio[0]:
            fin_prio, fin_state = prio, curr_state
            break

        def consume_states(it):
            nth = 0
            while True:
                next_state, from_tube, to_tube, count = next(it, (None, 0, 0, 0))
                if not next_state: break

                strstate = str(next_state)
                if strstate in parent: continue
                parent[strstate] = (prio, curr_state, (from_tube, to_tube, count))
                next_tup = prioritize_state(next_state)
                heappush(heap, next_tup)
                if need_print:
                    pretty_states_header(nth, len(next_state), str(next_tup[0]))
                yield next_state
            if need_print and nth % 3 != 0: stdout.write(linesep)

        if need_print:
            print("Next states:")
            pretty_states(consume_states(iter(next_states(curr_state))))
        else:
            iterable_len(consume_states(iter(next_states(curr_state))))

    if need_print:
        print()
        print("-------------------")
        print("Solution")
        print("-------------------")
        print()

    solutionbw = [(fin_prio, fin_state, (0, 0, 0))]
    while str(fin_state) in parent:
        solutionbw.append(parent[str(fin_state)])
        fin_state = parent[str(fin_state)][1]

    if need_print:
        for prio, res_state, ft in reversed(solutionbw):
            print(str(prio) + " " + str(ft))
            pretty_state(res_state)

    return reversed(solutionbw)


if __name__ == '__main__':
    start_state_main = [[]] * int(input("Tubes count: " if need_msg else ''))

    for i in range(len(start_state_main)):
        while len(start_state_main[i]) != 4:
            start_state_main[i] = input("{0}. tube elements: ".format(i + 1) if need_msg else '').split('.')

    solve_state(start_state_main, True)
