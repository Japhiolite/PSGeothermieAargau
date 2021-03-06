
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "WP2geo_modeling\03_POC_export-SHEMAT.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_WP2geo_modeling_03_POC_export-SHEMAT.py>`
        to download the full example code

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_WP2geo_modeling_03_POC_export-SHEMAT.py:


Create SHEMAT-Suite models
==========================
 
 With the MC ensemble of generated geological models stored in the respective lith-blocks, we can use them to create SHEMAT-Suite models for then doing 
 forward simulations of Heat- and Mass-transfer.

.. GENERATED FROM PYTHON SOURCE LINES 10-11

Libraries

.. GENERATED FROM PYTHON SOURCE LINES 11-21

.. code-block:: default

    import os,sys
    sys.path.append('../../')
    import OpenWF.shemat_preprocessing as shemsuite
    import glob
    import numpy as np
    import itertools as it
    import gempy as gp
    import pandas as pd
    print(f"Run with GemPy version {gp.__version__}")





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Run with GemPy version 2.2.9




.. GENERATED FROM PYTHON SOURCE LINES 22-27

load the base model
-------------------
For creating SHEMAT-Suite input files from the Monte Carlo Ensemble we created in :ref:`sphx_glr_examples_geo_modeling_02_POC_create-MC-ensemble.py` we load the base POC model, which was created
in :ref:`sphx_glr_examples_geo_modeling_01_POC_generate-model.py`. As we want to have the topography also in the SHEMAT-Suite model later on, we will create a mask of the model topography, called
`topo_mask`

.. GENERATED FROM PYTHON SOURCE LINES 27-35

.. code-block:: default



    model_path = '../../models/2021-06-04_POC_base_model'
    geo_model = gp.load_model('POC_PCT_model',
                             path=model_path, recompile=False)
    topo = geo_model._grid.topography.values.shape
    topo_mask = geo_model._grid.regular_grid.mask_topo





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Active grids: ['regular']
    Active grids: ['regular' 'topography']




.. GENERATED FROM PYTHON SOURCE LINES 36-39

Load the MC-lithologies
-----------------------
Next, we load the lithology blocks created by the MC example and mask them by the topography

.. GENERATED FROM PYTHON SOURCE LINES 39-47

.. code-block:: default


    lith_blocks = np.load('../../data/outputs/MCexample_10realizations.npy')

    lith_blocks_topo = np.array([])
    for i in lith_blocks:
        lith_blocks_topo = np.append(lith_blocks_topo, shemsuite.topomask(geo_model, i))
    lith_blocks_topo = lith_blocks_topo.reshape(len(lith_blocks), -1)








.. GENERATED FROM PYTHON SOURCE LINES 48-50

Now we prepared the lithologies, which are necessary for the `# uindex` field in a SHEMA-Suite input file, we can prepare the other parameters. Of which some are necessary, like the model
dimensions, and some are optional, like an array for the hydraulic head boundary condition, or observed data.

.. GENERATED FROM PYTHON SOURCE LINES 50-55

.. code-block:: default


    xmin, xmax, ymin, ymax, zmin, zmax = geo_model.grid.regular_grid.extent
    temp_data = '../../data/SHEMAT-Suite/all_boreholes_as_shemat_data.csv'









.. GENERATED FROM PYTHON SOURCE LINES 56-60

Set up the units for the SHEMAT-Suite model
-------------------------------------------
One core element of a SHEMAT-Suite Input file is the `# units` table. This table comprises the petrophysical parameters of the lithological units whose geometry is stored in the `# uindex` field.
The following code shows an example of how set up the `# units` table as a dataframe to be then stored in a SHEMAT-Suite input file. 

.. GENERATED FROM PYTHON SOURCE LINES 60-65

.. code-block:: default


    # Load existing units of the geological model:
    units = geo_model.surfaces.df[['surface', 'id']]
    units






.. raw:: html

    <div class="output_subarea output_html rendered_html output_result">
    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }

        .dataframe tbody tr th {
            vertical-align: top;
        }

        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>surface</th>
          <th>id</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>9</th>
          <td>Thrust1_south</td>
          <td>1</td>
        </tr>
        <tr>
          <th>10</th>
          <td>Thrust2_south</td>
          <td>2</td>
        </tr>
        <tr>
          <th>0</th>
          <td>Fault2</td>
          <td>3</td>
        </tr>
        <tr>
          <th>1</th>
          <td>Fault5</td>
          <td>4</td>
        </tr>
        <tr>
          <th>2</th>
          <td>Fault6</td>
          <td>5</td>
        </tr>
        <tr>
          <th>6</th>
          <td>Tertiary</td>
          <td>6</td>
        </tr>
        <tr>
          <th>8</th>
          <td>Pink</td>
          <td>7</td>
        </tr>
        <tr>
          <th>7</th>
          <td>Orange</td>
          <td>8</td>
        </tr>
        <tr>
          <th>5</th>
          <td>Unconformity</td>
          <td>9</td>
        </tr>
        <tr>
          <th>4</th>
          <td>Upper-filling</td>
          <td>10</td>
        </tr>
        <tr>
          <th>3</th>
          <td>Lower-filling</td>
          <td>11</td>
        </tr>
        <tr>
          <th>11</th>
          <td>basement</td>
          <td>12</td>
        </tr>
      </tbody>
    </table>
    </div>
    </div>
    <br />
    <br />

.. GENERATED FROM PYTHON SOURCE LINES 66-68

Now we create a dictionary with values for important parameters of each of the 12 units:
And join it with the existing units dataframe.

.. GENERATED FROM PYTHON SOURCE LINES 68-75

.. code-block:: default


    params = {'por': np.array([1e-10, 1e-10, 1e-10, 1e-10, 1e-10, 0.1, 0.05, 0.05, 0.01, 0.1, 0.05, 0.01]).T,
             'perm': np.array([1e-16, 1e-16, 1e-16, 1e-16, 1e-16, 1.0e-14, 1.0e-14, 1.0e-15, 1.0e-17, 1.0e-14, 1.0e-15, 1.0e-16]),
             'lz':   np.array([2.5, 2.5, 2.5, 2.5, 2.5, 2.3, 1.93, 2.9, 4.64, 2.03, 3.21, 3.1])}

    units = units.join(pd.DataFrame(params, index=units.index))








.. GENERATED FROM PYTHON SOURCE LINES 76-77

So now, the `units` table looks like this:

.. GENERATED FROM PYTHON SOURCE LINES 77-79

.. code-block:: default

    units






.. raw:: html

    <div class="output_subarea output_html rendered_html output_result">
    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }

        .dataframe tbody tr th {
            vertical-align: top;
        }

        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>surface</th>
          <th>id</th>
          <th>por</th>
          <th>perm</th>
          <th>lz</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>9</th>
          <td>Thrust1_south</td>
          <td>1</td>
          <td>1.000000e-10</td>
          <td>1.000000e-16</td>
          <td>2.50</td>
        </tr>
        <tr>
          <th>10</th>
          <td>Thrust2_south</td>
          <td>2</td>
          <td>1.000000e-10</td>
          <td>1.000000e-16</td>
          <td>2.50</td>
        </tr>
        <tr>
          <th>0</th>
          <td>Fault2</td>
          <td>3</td>
          <td>1.000000e-10</td>
          <td>1.000000e-16</td>
          <td>2.50</td>
        </tr>
        <tr>
          <th>1</th>
          <td>Fault5</td>
          <td>4</td>
          <td>1.000000e-10</td>
          <td>1.000000e-16</td>
          <td>2.50</td>
        </tr>
        <tr>
          <th>2</th>
          <td>Fault6</td>
          <td>5</td>
          <td>1.000000e-10</td>
          <td>1.000000e-16</td>
          <td>2.50</td>
        </tr>
        <tr>
          <th>6</th>
          <td>Tertiary</td>
          <td>6</td>
          <td>1.000000e-01</td>
          <td>1.000000e-14</td>
          <td>2.30</td>
        </tr>
        <tr>
          <th>8</th>
          <td>Pink</td>
          <td>7</td>
          <td>5.000000e-02</td>
          <td>1.000000e-14</td>
          <td>1.93</td>
        </tr>
        <tr>
          <th>7</th>
          <td>Orange</td>
          <td>8</td>
          <td>5.000000e-02</td>
          <td>1.000000e-15</td>
          <td>2.90</td>
        </tr>
        <tr>
          <th>5</th>
          <td>Unconformity</td>
          <td>9</td>
          <td>1.000000e-02</td>
          <td>1.000000e-17</td>
          <td>4.64</td>
        </tr>
        <tr>
          <th>4</th>
          <td>Upper-filling</td>
          <td>10</td>
          <td>1.000000e-01</td>
          <td>1.000000e-14</td>
          <td>2.03</td>
        </tr>
        <tr>
          <th>3</th>
          <td>Lower-filling</td>
          <td>11</td>
          <td>5.000000e-02</td>
          <td>1.000000e-15</td>
          <td>3.21</td>
        </tr>
        <tr>
          <th>11</th>
          <td>basement</td>
          <td>12</td>
          <td>1.000000e-02</td>
          <td>1.000000e-16</td>
          <td>3.10</td>
        </tr>
      </tbody>
    </table>
    </div>
    </div>
    <br />
    <br />

.. GENERATED FROM PYTHON SOURCE LINES 80-83

It is still missing the air component though. We have to add this, because the cells above the topography are
assigned to a unit representing the air. For mimicking the long-wavelength radiation outward from the ground, we assign
a high thermal conductivity to the air. If we were to assign a realistic low thermal conductivity, it would work as an insulator.

.. GENERATED FROM PYTHON SOURCE LINES 83-90

.. code-block:: default

    air = {'surface': 'air',
           'id': units.shape[0]+1,
          'por': 1e-10,
          'perm': 1e-22,
          'lz': 100}
    units = units.append(air, ignore_index=True)








.. GENERATED FROM PYTHON SOURCE LINES 91-96

Export to SHEMAT-Suite
----------------------
We are now all set for combining the lithology arrays, the `# units` table, temperature data from boreholes
into a SHEMAT-Suite input file. For this, we use the method `export_shemat_suite_input_file` in 
OpenWF.shemat_preprocessing.

.. GENERATED FROM PYTHON SOURCE LINES 96-107

.. code-block:: default


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



.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Successfully exported geological model POC_MC_0 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input
    Successfully exported geological model POC_MC_1 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input
    Successfully exported geological model POC_MC_2 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input
    Successfully exported geological model POC_MC_3 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input
    Successfully exported geological model POC_MC_4 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input
    Successfully exported geological model POC_MC_5 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input
    Successfully exported geological model POC_MC_6 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input
    Successfully exported geological model POC_MC_7 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input
    Successfully exported geological model POC_MC_8 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input
    Successfully exported geological model POC_MC_9 as SHEMAT-Suite input to ../../models/SHEMAT-Suite_input





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  1.476 seconds)


.. _sphx_glr_download_WP2geo_modeling_03_POC_export-SHEMAT.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: 03_POC_export-SHEMAT.py <03_POC_export-SHEMAT.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: 03_POC_export-SHEMAT.ipynb <03_POC_export-SHEMAT.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
