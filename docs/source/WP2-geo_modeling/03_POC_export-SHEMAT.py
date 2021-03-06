"""
Create SHEMAT-Suite models
==========================
 
 With the MC ensemble of generated geological models stored in the respective lith-blocks, we can use them to create SHEMAT-Suite models for then doing 
 forward simulations of Heat- and Mass-transfer.
"""

#%%
# Libraries
import os,sys
sys.path.append('../../')
import OpenWF.shemat_preprocessing as shemsuite
import glob
import numpy as np
import itertools as it
import gempy as gp
import pandas as pd
print(f"Run with GemPy version {gp.__version__}")

#%%
# load the base model
# -------------------
# For creating SHEMAT-Suite input files from the Monte Carlo Ensemble we created in :ref:`sphx_glr_examples_geo_modeling_02_POC_create-MC-ensemble.py` we load the base POC model, which was created
# in :ref:`sphx_glr_examples_geo_modeling_01_POC_generate-model.py`. As we want to have the topography also in the SHEMAT-Suite model later on, we will create a mask of the model topography, called
# `topo_mask`


model_path = '../../models/2021-06-04_POC_base_model'
geo_model = gp.load_model('POC_PCT_model',
                         path=model_path, recompile=False)
topo = geo_model._grid.topography.values.shape
topo_mask = geo_model._grid.regular_grid.mask_topo

#%%
# Load the MC-lithologies
# -----------------------
# Next, we load the lithology blocks created by the MC example and mask them by the topography

lith_blocks = np.load('../../data/outputs/MCexample_10realizations.npy')

lith_blocks_topo = np.array([])
for i in lith_blocks:
    lith_blocks_topo = np.append(lith_blocks_topo, shemsuite.topomask(geo_model, i))
lith_blocks_topo = lith_blocks_topo.reshape(len(lith_blocks), -1)

#%%
# Now we prepared the lithologies, which are necessary for the `# uindex` field in a SHEMA-Suite input file, we can prepare the other parameters. Of which some are necessary, like the model
# dimensions, and some are optional, like an array for the hydraulic head boundary condition, or observed data.

xmin, xmax, ymin, ymax, zmin, zmax = geo_model.grid.regular_grid.extent
temp_data = '../../data/SHEMAT-Suite/all_boreholes_as_shemat_data.csv'


#%% 
# Set up the units for the SHEMAT-Suite model
# -------------------------------------------
# One core element of a SHEMAT-Suite Input file is the `# units` table. This table comprises the petrophysical parameters of the lithological units whose geometry is stored in the `# uindex` field.
# The following code shows an example of how set up the `# units` table as a dataframe to be then stored in a SHEMAT-Suite input file. 

# Load existing units of the geological model:
units = geo_model.surfaces.df[['surface', 'id']]
units

#%%
# Now we create a dictionary with values for important parameters of each of the 12 units:
# And join it with the existing units dataframe.

params = {'por': np.array([1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 0.1, 0.05, 0.05, 0.01, 0.1, 0.05, 0.01]).T,
         'perm': np.array([1e-16, 1e-16, 1e-16, 1e-16, 1e-16, 1.0e-14, 1.0e-14, 1.0e-15, 1.0e-17, 1.0e-14, 1.0e-15, 1.0e-16]),
         'lz':   np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.3, 1.93, 2.9, 4.64, 2.03, 3.21, 3.1])}

units = units.join(pd.DataFrame(params, index=units.index))

#%%
# So now, the `units` table looks like this:
units

#%%
# It is still missing the air component though. We have to add this, because the cells above the topography are
# assigned to a unit representing the air. For mimicking the long-wavelength radiation outward from the ground, we assign
# a high thermal conductivity to the air. If we were to assign a realistic low thermal conductivity, it would work as an insulator.
air = {'surface': 'air',
       'id': units.shape[0]+1,
      'por': 1e-10,
      'perm': 1e-22,
      'lz': 100}
units = units.append(air, ignore_index=True)

#%%
# Export to SHEMAT-Suite
# ----------------------
# We are now all set for combining the lithology arrays, the `# units` table, temperature data from boreholes
# into a SHEMAT-Suite input file. For this, we use the method `export_shemat_suite_input_file` in 
# OpenWF.shemat_preprocessing.

shemade = ""
for c in range(len(lith_blocks_topo)):
    model = lith_blocks_topo[c,:]
    model_name = f"POC_MC_{c}"
    shemsuite.export_shemat_suite_input_file(geo_model, lithology_block=model, units=units,  
                                   data_file=temp_data,
                                   path='../../models/SHEMAT-Suite_input',
                                  filename=model_name)
    shemade += model_name + " \n"
with open("../../models/SHEMAT-Suite_input/shemade.job", 'w') as jobfile:
    jobfile.write(shemade)