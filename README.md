# Scheduling Algorithms Visualization

This Python script provides a real-time visualization of different scheduling algorithms using the `curses` library. It's designed to help understand how various scheduling algorithms (Rate Monotonic Scheduling, Deadline Monotonic Scheduling, Earliest Deadline First, and Least Laxity First) operate under different task configurations. This script was developed for my operating system 1 course that I give regular

## Features

- Real-time visualization of scheduling algorithms
- Support for Rate Monotonic Scheduling (RMS)
- Support for Deadline Monotonic Scheduling (DMS)
- Support for Earliest Deadline First (EDF)
- Support for Least Laxity First (LLF)
- Customizable task configurations
- Adjustable runtime and execution sleep time via command-line arguments

## Prerequisites

- Python 3.x
- A terminal emulator that supports `curses` (Linux and macOS terminals should work out of the box. Windows users might need to use WSL or Cygwin)

## Installation

1. Clone the repository or download the source code:
   ```bash
   git clone https://your-repository-url.git
   cd scheduling-algorithms-visualization
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

Note: This script has no external dependencies apart from standard Python libraries.

## Usage

To run the script with default settings (25 units of time, 1-second sleep, using RMS algorithm):
```bash
./sched-sim.py
```

To customize the runtime, sleep time, and algorithm:
```bash
./sched-sim.py -r 50 -s 0.5 -a edf
```
Options:
- `-r` or `--runtime`: Defines the simulation's duration in time units (default: 25).
- `-s` or `--sleep`: Sets the delay between each unit of time to slow down the visualization (default: 1 second).
- `-a` or `--algorithm`: Chooses the scheduling algorithm (`rms` for Rate Monotonic Scheduling, `dms` for Deadline Monotonic Scheduling, `edf` for Earliest Deadline First, `llf` for Least Laxity First).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs, feature requests, or improvements.

## License

[MIT License](LICENSE) - See the LICENSE file in the repository for more details.
