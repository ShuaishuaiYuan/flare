import sys
import numpy as np

from flare import otf, kernels
from flare.gp import GaussianProcess
from flare.mgp.mgp import MappedGaussianProcess
from flare.ase.calculator import FLARE_Calculator
import flare.mc_simple as mc_simple

# ---------- create gaussian process model -------------------
kernel = mc_simple.two_plus_three_body_mc
kernel_grad = mc_simple.two_plus_three_body_mc_grad
energy_force_kernel = mc_simple.two_plus_three_mc_force_en
energy_kernel = mc_simple.two_plus_three_mc_en

hyps = np.array([0.1, 1., 0.001, 1, 0.06])
two_cut = 5.0
three_cut = 5.0
cutoffs = np.array([two_cut, three_cut])
hyp_labels = ['sig2', 'ls2', 'sig3', 'ls3', 'noise']
opt_algorithm = 'BFGS'

gp_model = GaussianProcess(kernel, kernel_grad, hyps, cutoffs,
                           energy_kernel=energy_kernel,
                           energy_force_kernel=energy_force_kernel,
                           hyp_labels=hyp_labels,
                           opt_algorithm=opt_algorithm, par=False)

# ----------- create mapped gaussian process ------------------
struc_params = {'species': [47, 53],
                'cube_lat': np.eye(3) * 100,
                'mass_dict': {'0': 27, '1': 16}}

# grid parameters
lower_cut = 2.5
grid_num_2 = 16
grid_num_3 = 16
grid_params = {'bounds_2': [[lower_cut], [two_cut]],
               'bounds_3': [[lower_cut, lower_cut, 0],
                            [three_cut, three_cut, np.pi]],
               'grid_num_2': grid_num_2,
               'grid_num_3': [grid_num_3, grid_num_3, grid_num_3],
               'svd_rank_2': None,
               'svd_rank_3': None,
               'bodies': [2, 3],
               'load_grid': None,
               'update': True}

mgp_model = MappedGaussianProcess(gp_model, grid_params, struc_params,
                                 mean_only=True, lmp_file_name='agi.mgp')

# ------------ create ASE's flare calculator -----------------------
flare_calc = FLARE_Calculator(gp_model, mgp_model, par=False, use_mapping=True)
