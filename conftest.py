"""Garantit que la racine du projet est sur sys.path pour les tests,
quel que soit le mode d'invocation de pytest."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
