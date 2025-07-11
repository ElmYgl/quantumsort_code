# Quantum Sorting via Interference and Erasure

**Author:** Elmer Yglesias  
**Date:** July 11, 2025

This project demonstrates a novel approach to quantum sorting using interference, phase oracle marking, and Grover-style amplitude amplification.

## Features

# Quantum Sorting via Interference and Erasure

This project demonstrates a novel approach to quantum sorting using interference, phase oracle marking, and Grover-style amplitude amplification.

## Features

- Supports both fixed input (e.g., `[1, 0, 1]`) and full 3-qubit superpositions  
- Uses custom oracle logic to flip the phase of “sorted” bitstrings  
- Applies interference-based amplification (Grover diffusion)  
- Displays final sorted outcomes via Qiskit Aer simulation  
- Implements multi-pass variants through `quantum_search_2pass.py` and `quantum_search_3pass.py` scripts for enhanced sorting accuracy

## Scripts Overview

- **quantum_sort_ibm.py**: Core quantum sorting algorithm using single-pass Grover amplification  
- **quantum_search_2pass.py**: Two-pass quantum search variant for iterative refinement  
- **quantum_search_3pass.py**: Three-pass quantum search variant for improved precision in sorting  

## Requirements

- Python 3.8+  
- Qiskit  
- matplotlib

## Usage Examples

Run the core sorting algorithm on simulator with default settings:

```bash

python quantum_sort_ibm.py --backend simulator --shots 1024
python quantum_search_2pass.py --backend ibm_brisbane --iterations 2 --shots 2048
python quantum_search_3pass.py --backend ibm_brisbane --iterations 3 --shots 2048


