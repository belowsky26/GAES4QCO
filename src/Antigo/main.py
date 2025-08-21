from copy import deepcopy
from math import pi
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity
import random
import math
import numpy as np
import time
import json
from multiprocessing import Pool, cpu_count

#CROSSOVER = 75
#MUTATION = 12.5
CROSSOVER = 80
MUTATION = 8




