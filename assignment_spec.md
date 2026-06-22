# Tiny Digital Logic Simulator

Build a minimal combinational logic simulator that reads a single netlist
file, evaluates gates at given time points, and writes waveforms in a
WaveDrom-compatible JSON format.

Focus: parse a tiny text format, evaluate basic gates, and produce a clear
JSON waveform for wavedrom.com.  Go through the examples on the wavedrom.com website to see how to generate waveform input -- however you don't really need complex waveforms for this assignment, so keep it simple.

## Scope

- Combinational logic only (no memory, no clocks)
- Gates: AND, OR, NOT, XOR
- Inputs change at specific times; outputs are recomputed instantly
- One input file with four sections: INPUTS, OUTPUTS, GATES, STIMULUS

## Netlist Format

Plain text. One token or clause per space. Case-sensitive names. 

Any line where the first character that is not whitespace is `#` should be treated as a comment and completely skipped. `#` is not permitted anywhere after a non-space character.

Sections can appear in this fixed order.

```
# Tiny netlist example
INPUTS: A B
OUTPUTS: Y
GATES:
  # Syntax: OUT = GATE(IN1 [, IN2])
  Y = AND(A, B)
STIMULUS:
  # time  inputs in declared order
  0   0 0
  5   1 0
  10  1 1
  15  0 1
```

Rules:
- Signal names are alphanumeric with underscores (e.g., `A`, `sum_1`).
- `NOT` takes 1 input. `AND`, `OR`, `XOR` take exactly 2 inputs.
- Times are non-negative integers; rows must be in strictly increasing order.
- Input rows list values for all inputs in the order from `INPUTS:`.

Validation (keep friendly and simple):
- Reject unknown gates or mismatched input counts.
- Reject missing signals referenced in `GATES:`.
- Reject empty sections or unsorted/duplicate times.

## Evaluation Model

- For each row in `STIMULUS`, set input values, then evaluate all gates in a
  dependency-safe order (a simple topological order is fine).
- Record the final value of every input and output at each time.

## Output: WaveDrom JSON

Write a compact JSON that WaveDrom renders. Each `wave` character corresponds
to the row at the same index in `STIMULUS` (no spaces).

```
{
  "signal": [
    { "name": "A", "wave": "0110" },
    { "name": "B", "wave": "0011" },
    { "name": "Y", "wave": "0010" }
  ]
}
```

Conventions:
- Use only `0` and `1` characters with no spaces.
- The number of characters equals the number of `STIMULUS` rows.
- Order signals as: all inputs (in `INPUTS:` order), then outputs
  (in `OUTPUTS:` order).

## What To Build

- Program reads a `.net` text file (format above)
- Produces one file next to the input:
  - `<basename>.json` — WaveDrom JSON as specified

## Suggested Steps

- Parse sections and validate gently with clear error messages
- Build a DAG of gate dependencies; compute a stable order
- Evaluate on each `STIMULUS` row; collect values for inputs and outputs
- Write JSON exactly as shown in examples (for this assignment, only JSON is required)

## Example Inputs (Test Cases)

1) Simple AND

```
INPUTS: A B
OUTPUTS: Y
GATES:
  Y = AND(A, B)
STIMULUS:
  0  0 0
  1  0 1
  2  1 0
  3  1 1
```

Expected JSON

```
{
  "signal": [
    { "name": "A", "wave": "0011" },
    { "name": "B", "wave": "0101" },
    { "name": "Y", "wave": "0001" }
  ]
}
```

2) XOR then NOT

```
INPUTS: A B
OUTPUTS: Y
GATES:
  T = XOR(A, B)
  Y = NOT(T)
STIMULUS:
  0  0 0
  1  0 1
  2  1 1
  3  1 0
```

Expected JSON

```
{
  "signal": [
    { "name": "A", "wave": "0011" },
    { "name": "B", "wave": "0110" },
    { "name": "Y", "wave": "1010" }
  ]
}
```

3) OR then AND with NOT

```
INPUTS: A B C
OUTPUTS: Y
GATES:
  T1 = OR(A, B)
  T2 = NOT(C)
  Y  = AND(T1, T2)
STIMULUS:
  0  0 0 0
  1  1 0 0
  2  0 1 1
  3  0 0 1
```

Expected JSON

```
{
  "signal": [
    { "name": "A", "wave": "0100" },
    { "name": "B", "wave": "0010" },
    { "name": "C", "wave": "0011" },
    { "name": "Y", "wave": "0100" }
  ]
}
```

## Tips

- Keep parsing tolerant of extra spaces and blank lines
- Start with a single gate and two inputs; extend gradually
- Keep the spec tiny; avoid features not listed here

## Sample Solution and Examples

- Reference script: `digitalsim/digitalsim.py`
  - Run: `python digitalsim/digitalsim.py digitalsim/examples/and2.net`
  - Writes JSON next to the input (override with `-o out.json`)
- Example inputs and expected outputs are in `digitalsim/examples/`:
  - `and2.net` → `and2.json`
  - `xor_not.net` → `xor_not.json`
  - `or_and_not.net` → `or_and_not.json`
- Incorrect gate logic implementation  
- Missing dependency resolution
- Improper output formatting
- Not validating circuit connectivity

## To Submit

- A single ZIP file named rollno_A4.zip.
  - When unzipped, this should create a folder called rollno_A4, inside which should be the Python scripts along with a PDF file.
  - No extra files such as __MACOS files, .DS_Store, .Trash etc. should be present.
  - If you add any extra test cases, make sure your program can still be run with just the normal instructions above.  Give clear instructions on how to run the extra tests.
- The PDF file should contain a 1-2 page report explaining how you have solved the problem - were there any specific algorithms you needed to look up, did you use the help of online resources or other friends/LLMs etc.  You are expected to work on your own, but if you do consult other sources for understanding the problem, please report it here for completeness.  This will NOT be penalized, but if your code is found to be directly copied or obtained from outside sources, there WILL be penalties.
- The Python script named digitalsim.py should be in a state where it can be run as shown in the examples above to test with different inputs.  You need to look at how the argparse implementation is done and make sure your code follows that.
