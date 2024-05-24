#!/usr/bin/env python

import curses
import time
import sys

from collections import deque
from argparse import ArgumentParser


class Scheduler:
    process_id = 0

    def __init__(self, name, color, release, execution, deadline, period):
        self.name = name
        self.color = color
        self.release = release
        self.execution = execution
        self.deadline = deadline
        self.period = period
        self.vruntime = 0

        # set first period to release
        self.current_period = self.release
        self.current_deadline = self.deadline

        Scheduler.process_id += 2
        self.process_id = Scheduler.process_id - 1

    def check_completed(self):
        if self.vruntime == self.execution:
            self.vruntime = 0
            self.current_period += self.period
            self.current_deadline += self.deadline

    def is_ready(self, t):
        return t >= self.current_period

    def deadline_missed(self, t):
        if (self.current_deadline - self.vruntime - t) < 0:
            return True

        return False

    def __repr__(self):
        return "(%s | %s | %s | %s)" % (self.name, self.vruntime, self.current_period, self.period)

    def draw(self, stdscr, time, nr_of_tasks):
        # increase vruntime
        self.vruntime += 1

        # set color
        # Define a color pair (foreground color, background color)
        curses.init_pair(self.process_id, curses.COLOR_WHITE, self.color)
        color = curses.color_pair(self.process_id)

        # Draw the box (a single character space)
        stdscr.addstr(self.process_id, time, self.name, color)

        # Draw the
        stdscr.addstr(nr_of_tasks*2 + 5, time, self.name, color)

        # Refresh the screen to see the changes
        stdscr.refresh()


# Rate Monotonic Scheduling (RMS)
class Rms(Scheduler):

    def sorting_criteria(self, t):
        return self.period


# Deadline Monotonic Scheduling (DMS)
class Dms(Scheduler):

    def sorting_criteria(self, t):
        return self.deadline


# Earliest Deadline First (EDF)
class Edf(Scheduler):

    def distance_deadline(self, t):
        return self.current_deadline - t

    def sorting_criteria(self, t):
        return self.distance_deadline(t)


# Least Laxity First (LLF)
class Llf(Scheduler):

    def laxity(self, t):
        return self.current_deadline - self.execution - t

    def sorting_criteria(self, t):
        return self.laxity(t)


def prepare_screen(stdscr, args, tasks):
    # Clear screen
    stdscr.clear()

    # Title
    stdscr.addstr('Scheduling Algorithm: ')
    stdscr.addstr(args['algo'])

    curses.start_color()

    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_RED)

    # Draw timeline for each task
    for task in tasks:
        for x in range(0, args["runtime"]):
            if (x % task.deadline) == 0 and x != 0:
                stdscr.attron(curses.color_pair(10))
            if (x % 5) == 0:
                stdscr.addch(task.process_id + 1, x, "|")
            else:
                stdscr.addch(task.process_id + 1, x, "-")

            stdscr.attroff(curses.color_pair(10))


def main(stdscr, args, tasks):
    prepare_screen(stdscr, args, tasks)

    for t in range(0, args['runtime']):
        queue = deque()
        for task in tasks:
            if task.is_ready(t):
                queue.append(task)

        time.sleep(args['sleep'])

        sorted_queue = sorted(queue, key=lambda x: x.sorting_criteria(t))

        # check if we really have tasks that can be executed
        if sorted_queue:
            sorted_queue[0].draw(stdscr, t, len(tasks))
            for task in tasks:
                if task.deadline_missed(t):
                    print(task.name + " missed the deadline at " + str(t))
                    stdscr.getch()
            sorted_queue[0].check_completed()

    stdscr.getch()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-r", "--runtime", dest="runtime", type=int, default=25,
                        help="Runtime defines how long Scheduler to simulate")
    parser.add_argument("-s", "--sleep", dest="sleep", type=float, default=1,
                        help="time to sleep during the execution")
    parser.add_argument("-a", "--algorithm", dest="algo", default='rms',
                        help="Runtime defines how long Scheduler to simulate")

    args = vars(parser.parse_args())

    # Create dynamic class for the scheduling algorithm
    Obj = getattr(sys.modules[__name__], args['algo'].title())
    scheduling_algo = type(args['algo'].title(), (Obj,), {})

    # Task Information
    tasks = [                                    # r  e  d   p
        scheduling_algo("A", curses.COLOR_BLUE,    0, 1, 3, 3),
        scheduling_algo("B", curses.COLOR_MAGENTA, 0, 1, 4, 4),
        scheduling_algo("C", curses.COLOR_GREEN,   0, 2, 5, 5),
    ]

    curses.wrapper(main, args, tasks)
