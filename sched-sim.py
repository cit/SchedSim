#!/usr/bin/env python

import curses
import time
import sys

from collections import deque
from argparse import ArgumentParser


class Scheduler:
    process_id = 0
    long_name = ''

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
        self.current_deadline = self.release + self.deadline

        Scheduler.process_id += 3
        self.process_id = Scheduler.process_id - 1

    def check_completed(self):
        if self.vruntime == self.execution:
            self.vruntime = 0
            self.current_period += self.period
            self.current_deadline = self.current_period + self.deadline

    def is_ready(self, t):
        return t >= self.current_period

    def deadline_missed(self, t):
        # print(self.current_deadline - self.vruntime - t)
        if (self.current_deadline - self.vruntime - t) == 0:
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
        stdscr.addstr(nr_of_tasks*3 + 5, time, self.name, color)

        # Refresh the screen to see the changes
        stdscr.refresh()


# Rate Monotonic Scheduling (RMS)
class Rms(Scheduler):
    long_name = 'Rate Monotonic Scheduling (RMS)'

    def sorting_criteria(self, t):
        return self.period


# Deadline Monotonic Scheduling (DMS)
class Dms(Scheduler):
    long_name = 'Deadline Monotonic Scheduling (DMS)'

    def sorting_criteria(self, t):
        return self.deadline


# Earliest Deadline First (EDF)
class Edf(Scheduler):
    long_name = 'Earliest Deadline First (EDF)'

    def distance_deadline(self, t):
        return self.current_deadline - t

    def sorting_criteria(self, t):
        return self.distance_deadline(t)


# Least Laxity First (LLF)
class Llf(Scheduler):
    long_name = 'Least Laxity First (LLF)'

    def laxity(self, t):
        return self.current_deadline - self.execution - t

    def sorting_criteria(self, t):
        return self.laxity(t)


def prepare_screen(stdscr, args, tasks):
    # Clear screen
    stdscr.clear()

    # Title
    stdscr.addstr('Scheduling Algorithm: ')
    stdscr.addstr(tasks[0].long_name)

    red_color = 10

    curses.init_pair(red_color, curses.COLOR_WHITE, curses.COLOR_RED)

    # Draw timeline for each task
    for task in tasks:
        for x in range(0, args["runtime"]):
            color = curses.color_pair(0)
            if ((x - task.release - task.deadline) % task.period) == 0 and x > task.release:
                color = curses.color_pair(10)

            if (x % 5) == 0:
                stdscr.addstr(task.process_id + 1, x, "|", color)
                stdscr.addstr(task.process_id + 2, x, str(x))
            else:
                stdscr.addch(task.process_id + 1, x, "-", color)

    max_y, max_x = stdscr.getmaxyx()

    # Define the start position on the right side
    start_x = max_x - 30
    start_y = 0

    stdscr.addstr(start_y, start_x, "Task Information")
    stdscr.addstr(start_y + 2, start_x, "    r   e   d   p")

    for i, task in enumerate(tasks):
        stdscr.addstr(start_y + i + 3, start_x,
                      task.name +
                      '{:4d}'.format(task.release) +
                      '{:4d}'.format(task.execution) +
                      '{:4d}'.format(task.deadline) +
                      '{:4d}'.format(task.period))

    stdscr.refresh()


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
            sorted_queue[0].check_completed()

            for task in tasks:
                if task.deadline_missed(t):
                    print(task.name + " missed the deadline at " + str(t))
                    stdscr.getch()
                    if stdscr.getch() == ord('q'):
                        sys.exit(0)

    stdscr.getch()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-r", "--runtime",
                        dest="runtime",
                        type=int,
                        default=25,
                        help="Defines how long the Scheduler should simulate.")
    parser.add_argument("-s", "--sleep",
                        dest="sleep",
                        type=float,
                        default=1,
                        help="Time in seconds to sleep during the execution.")
    parser.add_argument("-a", "--algorithm",
                        dest="algo",
                        default='rms',
                        choices=['rms', 'dms', 'edf', 'llf'],
                        help="Select the scheduling algorithm to use.")

    args = vars(parser.parse_args())

    # Create dynamic class for the scheduling algorithm
    Obj = getattr(sys.modules[__name__], args['algo'].title())
    scheduling_algo = type(args['algo'].title(), (Obj,), {})

    # Task Information
    tasks = [                                    # r  e  d   p
        scheduling_algo("A", curses.COLOR_BLUE,    0, 1, 3, 3),
        scheduling_algo("B", curses.COLOR_MAGENTA, 0, 1, 4, 4),
        scheduling_algo("C", curses.COLOR_GREEN,   1, 2, 5, 5),
    ]

    curses.wrapper(main, args, tasks)
