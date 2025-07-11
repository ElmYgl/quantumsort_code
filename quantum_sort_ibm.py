"""
Quantum Interference Sort — Grover “Eraser” Demo  (robust hardware build)
Author : Elmer Yglesias • 7 Jul 2025
"""

from __future__ import annotations
import argparse
from collections import Counter
from typing import Any, List

from qiskit_aer import Aer
from qiskit import QuantumCircuit, transpile

try:
    from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
except ImportError:
    QiskitRuntimeService = None  # type: ignore
    Sampler = None               # type: ignore

TARGET_STATE      = "011"
NUM_GROVER_ITERS  = 2
DEFAULT_TRIALS    = 1
DEFAULT_SHOTS     = 1024
DEFAULT_BACKEND   = "ibm_brisbane"

# ── Grover helpers ──────────────────────────────────────────────────────
def apply_oracle(qc: QuantumCircuit) -> None:
    qc.x(2); qc.h(0); qc.ccx(1, 2, 0); qc.h(0); qc.x(2)

def apply_diffusion(qc: QuantumCircuit) -> None:
    qc.h([0,1,2]); qc.x([0,1,2]); qc.h(2); qc.ccx(0,1,2)
    qc.h(2); qc.x([0,1,2]); qc.h([0,1,2])

def build_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3)
    qc.h([0, 1, 2])
    for _ in range(NUM_GROVER_ITERS):
        apply_oracle(qc)
        apply_diffusion(qc)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

# ── utilities ───────────────────────────────────────────────────────────
def _to_bits(key: Any) -> str:
    if isinstance(key, str):
        return key
    try:
        return key.to01()  # BitArray
    except AttributeError:
        try:
            return ''.join(str(int(b)) for b in key)  # iterable of 0/1
        except Exception:
            return str(key)

def _bitarray_to_strings(bitarr) -> List[str]:
    """
    Convert BitArray shots to list[str].

    Handles:
    • [[0,1,1], ...]   → '011'
    • [[3], [0], ...]  → '011', '000', ...
    • [3, 0, 7, ...]   → decimal ints → 3-bit strings
    """
    # Preferred path: modern BitArray has .tolist()
    if hasattr(bitarr, "tolist"):
        rows = bitarr.tolist()
    else:
        # Access the underlying ndarray safely
        rows = getattr(bitarr, "_array", None)
        if rows is None:
            rows = getattr(bitarr, "array", None)
        if rows is None:
            raise RuntimeError("Unrecognised BitArray internals.")
        rows = rows.tolist()

    width = getattr(bitarr, "num_bits", 3)
    strings: List[str] = []
    for sample in rows:
        # Raw bits list/tuple
        if isinstance(sample, (list, tuple)) and len(sample) == width:
            strings.append(''.join(str(int(b)) for b in sample))
        # One-element list with an int inside
        elif isinstance(sample, (list, tuple)) and len(sample) == 1:
            strings.append(format(int(sample[0]), f"0{width}b"))
        # Bare int (0–7)
        elif isinstance(sample, int):
            strings.append(format(sample, f"0{width}b"))
        else:
            raise RuntimeError(f"Unexpected BitArray row: {sample!r}")
    return strings

# ── main runner ─────────────────────────────────────────────────────────
def run(trials: int, shots: int, *, hw: bool, backend_name: str) -> None:

    if hw:
        if QiskitRuntimeService is None:
            raise ImportError("Install qiskit-ibm-runtime for hardware mode.")
        svc = QiskitRuntimeService()
        backend = svc.backend(backend_name)
        sampler = Sampler(backend)  # direct mode; Open Plan–compatible
        print(f"🛰️  Backend: {backend.name} ({backend.configuration().n_qubits} qubits)")
    else:
        backend = Aer.get_backend("aer_simulator")
        sampler = None  # type: ignore
        print("🖥️  Local Aer simulator")

    aggregated = Counter()
    for _ in range(trials):
        qc = build_circuit()

        if hw:
            tqc = transpile(qc, backend, optimization_level=3)
            raw = sampler.run([tqc], shots=shots).result()

            # Old-style QuasiDistribution
            if hasattr(raw, "quasi_dists") or hasattr(raw, "quasi_distributions"):
                q = raw.quasi_dists[0] if hasattr(raw, "quasi_dists") else raw.quasi_distributions[0]
                counts = {
                    _to_bits(k): int(round(p * shots))
                    for k, p in zip(q.keys(), q.probabilities())
                }
            else:
                # New SamplerPubResult with BitArray
                pub = raw[0]
                bitarr = pub.data["c"]
                counts = Counter(_bitarray_to_strings(bitarr))
        else:
            job_res = backend.run(transpile(qc, backend), shots=shots).result()
            counts = job_res.get_counts()

        aggregated.update(counts)
        print("Trial:", counts)

    total = trials * shots
    print("\nAggregated results:")
    for bit, cnt in sorted(aggregated.items(), key=lambda kv: kv[1], reverse=True):
        pct = 100 * cnt / total
        mark = "✅" if bit == TARGET_STATE else ""
        print(f"  {bit}: {cnt} ({pct:.2f} %) {mark}")

    success_pct = 100 * aggregated.get(TARGET_STATE, 0) / total
    print(f"\n✅ Amplification for “{TARGET_STATE}”: {success_pct:.2f} % over {total} shots")

# ── CLI ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grover eraser sort — Aer / IBM QPU")
    parser.add_argument("--hardware", action="store_true", help="Run on IBM hardware")
    parser.add_argument("--backend", default=DEFAULT_BACKEND, help="Backend name")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS, help="Repeat count")
    parser.add_argument("--shots", type=int, default=DEFAULT_SHOTS, help="Shots per job")
    cli = parser.parse_args()

    run(cli.trials, cli.shots, hw=cli.hardware, backend_name=cli.backend)

