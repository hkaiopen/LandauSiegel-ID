"""
Landau-Siegel Zero Detection — Phase 1 & 2 Combined
=====================================================
1. Scan L-functions for zeros near s=1
2. Apply global constraint analysis using coupling matrix K1
"""

import numpy as np
from scipy.special import gamma

# ====================== Phase 1: Data Generation ======================
def primitive_dirichlet_characters(modulus):
    """Generate all primitive Dirichlet characters modulo q."""
    characters = []
    for n in range(1, modulus):
        if np.gcd(n, modulus) == 1:
            char_vals = {}
            for k in range(modulus):
                char_vals[k] = np.exp(2j * np.pi * n * k / modulus)
            characters.append(char_vals)
    return characters

def L_function_approx(s, chi, q, terms=5000):
    """Compute Dirichlet L-function L(s, chi) via series expansion."""
    result = 1.0 + 0j
    for n in range(2, terms):
        if np.gcd(n, q) == 1:
            result += chi[n % q] / (n ** s)
    return result

def L_function_derivative(s, chi, q, terms=5000, h=1e-6):
    """Finite difference approximation of L'(s, chi)."""
    return (L_function_approx(s + h, chi, q, terms) - 
            L_function_approx(s - h, chi, q, terms)) / (2 * h)

def find_zero_near(s0, chi, q, max_iter=50, tol=1e-10):
    """Find a zero of L(s, chi) near s0 using Newton's method."""
    s = s0
    for _ in range(max_iter):
        L_val = L_function_approx(s, chi, q)
        L_deriv = L_function_derivative(s, chi, q)
        if abs(L_deriv) < 1e-12:
            break
        s_new = s - L_val / L_deriv
        if abs(s_new - s) < tol:
            return s_new
        s = s_new
    return s

# ====================== Phase 2: Global Constraint Analysis ======================
def coupling_matrix_K1(s, q):
    """Generalized coupling matrix for Dirichlet L-functions."""
    t = abs(s.imag)
    if t < 1e-10:
        t = 1.0
    return np.sqrt(2 * np.log(q * t / (2 * np.pi) + 1))

def constraint_potential(zero_list, q):
    """Compute the global constraint potential on zero distribution."""
    potential = 0.0
    for zero in zero_list:
        t = abs(zero.imag)
        if t < 1e-10:
            dist_from_1 = 1.0 - zero.real
            if dist_from_1 < 0.5:
                K1 = coupling_matrix_K1(zero, q)
                potential += np.exp(-K1 * dist_from_1)
    return potential

# ====================== Main Execution ======================
print("Landau-Siegel Zero Detection — Phase 1: Scanning s near 1")
print("=" * 60)

moduli = list(range(3, 51))
results = []

for q in moduli:
    chi_list = primitive_dirichlet_characters(q)
    for chi in chi_list:
        for delta in np.logspace(-5, 0, 100):
            s_candidate = 1.0 - delta
            L_val = L_function_approx(s_candidate, chi, q, terms=3000)
            
            if abs(L_val) < 0.1:
                zero = find_zero_near(s_candidate, chi, q)
                if zero is not None and 0.5 < zero.real < 1.01 and abs(zero.imag) < 1.0:
                    results.append((q, zero, chi))
                    print(f"  q={q}: possible zero at s = {zero.real:.10f} + {zero.imag:.10f}i")

print(f"\nPhase 1 scan complete. {len(results)} candidate zeros found.")

# ---- Phase 2: Global Constraint Analysis ----
print("\nPhase 2: Global Constraint Analysis")
print("=" * 50)

for q in moduli:
    zeros_for_q = [res[1] for res in results if res[0] == q]
    if zeros_for_q:
        V = constraint_potential(zeros_for_q, q)
        print(f"  q={q}: constraint potential V = {V:.6e}")
    else:
        print(f"  q={q}: no zeros found (potential V = 0)")