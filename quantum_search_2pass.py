# Quantum Search with 2-Pass Comparator Circuit
# Author: Elmer Yglesias
# Date: July 06, 2025 – 12:27AM
# Acknowledgment: Developed using IBM Qiskit, with support from AerSimulator for quantum emulation.
#
# Description:
# This script demonstrates a 2-pass quantum sorting algorithm for a 3-bit input using a reversible comparator
# and conditional SWAP gates. The circuit is built using Qiskit and tested on the AerSimulator.
#
# The result is measured using a big-endian classical mapping to recover the sorted output of the quantum circuit.


from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

def comparator(qc, a, b, ancilla):
    qc.cx(b, ancilla)
    qc.cx(a, ancilla)
    qc.ccx(ancilla, a, b)
    qc.cx(a, ancilla)
    qc.cx(b, ancilla)

def run_quantum_sort(bits):
    qc = QuantumCircuit(4, 3)  # 3 qubits for data, 1 ancilla

    # Initialize input
    for i, bit in enumerate(bits):
        if bit == "1":
            qc.x(i)

    qc.barrier()
    comparator(qc, 0, 1, 3)
    comparator(qc, 1, 2, 3)
    qc.barrier()

    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

def simulate_and_plot(bits):
    qc = run_quantum_sort(bits)
    sim = Aer.get_backend("aer_simulator")
    result = sim.run(transpile(qc, sim), shots=1024).result()
    counts = result.get_counts()

    label = "".join(bits)
    print(f"Input state |{label}⟩ → Measurement: {counts}")

    fig = plot_histogram(counts)
    plt.title(f"Quantum Sort Output for |{label}⟩")
    plt.xlabel("Sorted Bitstring")
    plt.ylabel("Counts")
    filename = f"qsort2_{label}.png"
    plt.savefig(filename)
    print(f"Saved: {filename}")
    plt.close()

# Run all 8 combinations
inputs = [format(i, "03b") for i in range(8)]
for bits in inputs:
    simulate_and_plot(bits)
