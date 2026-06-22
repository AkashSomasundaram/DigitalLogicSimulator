"""Tiny combinational logic simulator producing WaveDrom JSON.

Usage:
  python digitalsim.py path/to/circuit.net [--out out.json]

Input format sections (fixed order): INPUTS, OUTPUTS, GATES, STIMULUS.
Gates: OUT = AND(A, B) | OR(A, B) | XOR(A, B) | NOT(A)

Note: this template file uses the `argparse` module to get arguments
from the command line.  You are expected to retain this part of it
to make testing easier.  The function calls given in the `main` function
are only suggestions, and you can rename them or create others as long
as the interface to the outside world does not change.

This may make it a bit harder to run purely from an editor like VSCode. 
However, in practice you almost never run code directly from an editor,
so this is something you need to be able to handle anyway.
"""

import sys
import argparse
from pathlib import Path
import re
import json
from typing import List, Tuple, Dict

Gate = Tuple[str, str, Tuple[str, ...]]


class Circuit:
    """Container for parsed netlist information."""
    def __init__(self):
        self.inputs: List[str] = []
        self.outputs: List[str] = []
        self.gates: List[Gate] = []
        self.stimuli: List[Tuple[int, List[int]]] = []


def parse_netlist(text: str) -> Circuit:
    """Parse .net text and return a Circuit object."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]

    def check_section(expected: str, i: int) -> int:
        if i >= len(lines) or not lines[i].startswith(expected):
            raise ValueError(f"Expected section '{expected}' not found")
        return i

    circ = Circuit()

    # INPUTS
    i = check_section("INPUTS:", 0)
    circ.inputs = lines[i].split(":", 1)[1].split()
    i += 1

    # OUTPUTS
    i = check_section("OUTPUTS:", i)
    circ.outputs = lines[i].split(":", 1)[1].split()
    i += 1

    # GATES
    i = check_section("GATES:", i)
    i += 1

    pat = re.compile(
        r"^(?P<out>\w+)\s*=\s*(?P<op>AND|OR|XOR|NOT)\s*\((?P<args>[\w,\s]+)\)$"
    )

    while i < len(lines) and not lines[i].startswith("STIMULUS:"):
        m = pat.match(lines[i])
        if not m:
            raise ValueError(f"Invalid gate definition: {lines[i]}")
        out = m.group("out")
        op = m.group("op")
        ins = tuple(a.strip() for a in m.group("args").split(","))
        circ.gates.append((out, op, ins))
        i += 1

    # STIMULUS
    circ.stimuli = []
    if i < len(lines) and lines[i].startswith("STIMULUS:"):
        i += 1
        while i < len(lines):
            t, *vals = lines[i].split()
            circ.stimuli.append((int(t), [int(v) for v in vals]))
            i += 1

    return circ


def eval_gate(op: str, values: Tuple[int, ...]) -> int:
    """Compute logic output for given gate and input values."""
    if op == "AND":
        if len(values) != 2:
            raise ValueError("AND expects 2 inputs")
        return values[0] & values[1]
    if op == "OR":
        if len(values) != 2:
            raise ValueError("OR expects 2 inputs")
        return values[0] | values[1]
    if op == "XOR":
        if len(values) != 2:
            raise ValueError("XOR expects 2 inputs")
        return values[0] ^ values[1]
    if op == "NOT":
        if len(values) != 1:
            raise ValueError("NOT expects 1 input")
        return 1 - values[0]
    raise ValueError(f"Unknown gate type: {op}")



def simulate(circ: Circuit) -> Dict[str, List[int]]:
    """Run logic simulation and return waveforms, handling any gate order."""
    signals = list(dict.fromkeys(circ.inputs + [g[0] for g in circ.gates] + circ.outputs))
    traces = {s: [] for s in signals}

    for t, inputs in circ.stimuli:
        # Initialize state with input values
        state = {name: val for name, val in zip(circ.inputs, inputs)}
        remaining = circ.gates.copy()
        solved_last_round = -1  # to detect deadlock

        # Keep looping until all gates are resolved or no progress
        while remaining and len(remaining) != solved_last_round:
            solved_last_round = len(remaining)
            next_remaining = []

            for out, op, ins in remaining:
                # Check if all input signals are already known
                if all(n in state for n in ins):
                    vals = tuple(state[n] for n in ins)
                    state[out] = eval_gate(op, vals)
                else:
                    next_remaining.append((out, op, ins))

            remaining = next_remaining

        # If there are still unsolved gates, dependency issue (e.g. feedback loop)
        if remaining:
            raise ValueError(
                f"Cannot resolve circuit dependencies. Possibly cyclic or undefined signals: {remaining}"
            )

        # Record signal values for this timestep
        for s in signals:
            traces[s].append(state.get(s, 0))

    return traces



def make_wavedrom_json(traces: Dict[str, List[int]]) -> str:
    """Convert waveforms dict to WaveDrom-compatible JSON."""
    data = {"signal": []}
    for sig, vals in traces.items():
        data["signal"].append({"name": sig, "wave": "".join(map(str, vals))})
    return json.dumps(data, indent=2)


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("netlist", help="Path to .net file")
    parser.add_argument("--out", "-o", help="Output JSON path")
    args = parser.parse_args(argv)

    net_text = Path(args.netlist).read_text()
    circuit = parse_netlist(net_text)
    result = simulate(circuit)
    json_out = make_wavedrom_json(result)

    out_file = args.out or str(Path(args.netlist).with_suffix(".json"))
    Path(out_file).write_text(json_out + "\n")
    print(out_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
