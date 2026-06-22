# Digital Logic Simulator

A Python-based combinational circuit simulator that parses digital logic netlists, evaluates gate dependencies, and generates WaveDrom-compatible JSON waveforms.

## Features

* Supports **AND**, **OR**, **XOR**, and **NOT** gates
* Parses structured netlist files
* Handles arbitrary gate ordering through dependency-aware evaluation
* Detects cyclic and undefined signal dependencies
* Generates WaveDrom-compatible JSON output for waveform visualization
* Includes example circuits and expected outputs

## Repository Structure

```text
DigitalLogicSimulator/
├── digitalsim.py          # Main simulator
├── assignment_spec.md     # Original assignment specification
├── report.pdf             # Project report
├── examples/
│   ├── and2.net
│   ├── and2.json
│   ├── xor_not.net
│   ├── xor_not.json
│   ├── or_and_not.net
│   ├── or_and_not.json
│   ├── complex4.net
│   └── complex4.json
└── .gitignore
```

## Netlist Format

```text
INPUTS: A B
OUTPUTS: Y

GATES:
Y = AND(A, B)

STIMULUS:
0 0 0
1 0 1
2 1 0
3 1 1
```

Supported gates:

* AND
* OR
* XOR
* NOT

## Usage

Run the simulator on a netlist file:

```bash
python digitalsim.py examples/and2.net
```

The simulator generates a JSON waveform file alongside the input netlist.

To specify an output file:

```bash
python digitalsim.py examples/and2.net -o output.json
```

## Example Output

```json
{
  "signal": [
    { "name": "A", "wave": "0011" },
    { "name": "B", "wave": "0101" },
    { "name": "Y", "wave": "0001" }
  ]
}
```

The generated JSON can be visualized using WaveDrom.

## Implementation

The simulator models combinational circuits as a dependency graph. For each stimulus step, input values are assigned and gates whose inputs are already known are evaluated. This process repeats until all signals have been resolved, ensuring correct evaluation regardless of the order in which gates appear in the netlist.

## Author

Akash Somasundaram
B.Tech Electrical Engineering, IIT Madras
