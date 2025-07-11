# Quantum Search with 3-Pass Comparator Circuit
# Author: Elmer Yglesias
# Date: July 06, 2025 – 12:27AM
# Acknowledgment: Developed using IBM Qiskit, with support from AerSimulator for quantum emulation.
#
# Description:
# This script demonstrates a 3-pass quantum sorting algorithm for a 3-bit input using a reversible comparator
# and conditional SWAP gates. The circuit is built using Qiskit and tested on the AerSimulator.
#
# The result is measured using a big-endian classical mapping to recover the sorted output of the quantum circuit.


from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# 🧠 Custom comparator: compare q[i] and q[j] using ancilla qubits (anc_notj and anc_cond)
def compare_and_swap(qc, i, j, anc_notj, anc_cond):
    print(f"🔁 Compare-and-Swap: q[{i}] vs q[{j}] using ancillas q[{anc_notj}], q[{anc_cond}]")
    # anc_notj = NOT q[j]
    qc.x(j)
    qc.cx(j, anc_notj)
    qc.x(j)  # restore

    # anc_cond = q[i] AND anc_notj (i > j)
    qc.ccx(i, anc_notj, anc_cond)

    # Conditional SWAP if i > j
    qc.cswap(anc_cond, i, j)

    # Uncompute
    qc.ccx(i, anc_notj, anc_cond)
    qc.cx(j, anc_notj)

# 🧮 Main sorting logic
def quantum_sort_3pass(input_bits):
    print(f"🚀 Initializing circuit with input bits: {input_bits}")
    qc = QuantumCircuit(5, 5)  # 3 data + 2 ancilla, all measured

    # Load initial bits into q[0], q[1], q[2]
    for idx, bit in enumerate(input_bits):
        if bit == 1:
            qc.x(idx)

    # Compare-and-swap passes (bubble sort)
    compare_and_swap(qc, 0, 1, 3, 4)  # Pass 1
    compare_and_swap(qc, 1, 2, 3, 4)  # Pass 2
    compare_and_swap(qc, 0, 1, 3, 4)  # Pass 3

    qc.barrier()
    qc.measure([0, 1, 2, 3, 4], [4, 3, 2, 1, 0])  # Big-endian ordering for Qiskit

    return qc

# 🧪 Run simulation
input_bits = [1, 0, 1]
qc = quantum_sort_3pass(input_bits)
print("\n🧠 Quantum Circuit:")
print(qc.draw(output="text"))

simulator = AerSimulator()
compiled = transpile(qc, simulator)
result = simulator.run(compiled, shots=1024).result()
counts = result.get_counts()

print("\n📊 Sorted result (measured):", counts)
plot_histogram(counts)
plt.show()

# 🔍 Analyze result: Extract bits from correct classical registers (c[4], c[3], c[2]) = q[0], q[1], q[2]
most_common = max(counts, key=counts.get)  # e.g. '01101'
print("\n✨ Extracting the Sorted Output")
print("We only care about the data qubits: q[0], q[1], q[2].")
print(f"From the string '{most_common}':")

# Correct big-endian extraction from classical bits c[4], c[3], c[2]
sorted_q = [
    int(most_common[4]),  # c[4] = q[0]
    int(most_common[3]),  # c[3] = q[1]
    int(most_common[2])   # c[2] = q[2]
]

print(f"q[0] → {sorted_q[0]}")
print(f"q[1] → {sorted_q[1]}")
print(f"q[2] → {sorted_q[2]}")

print("\n✅ Final Sorted Result:")
print(f"[q[0], q[1], q[2]] = {sorted_q}")
