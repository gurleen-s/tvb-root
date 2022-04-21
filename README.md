
# The Virtual Brain

This repository holds the python sources for TVB main codebase. Install using:
  1. Clone repo
  2. Create dedicated Python env
  3. Navigate to **tvb_build** and input the following command:
    
        sh install_full_tvb.sh

"The Virtual Brain" Project (TVB Project) has the purpose of offering 
modern tools to the Neurosciences community, for computing, simulating
and analyzing functional and structural data of human brains, brains modeled 
at the  level of population of neurons.

## Contents
0. Intro and main install
1. Additional packages needing installation
2. Jupyter notebook installation and tutorials
3. Explanation of Library
    3a. TVB Scientific library (tvb-library)
    3b. TVB Framework (tvb-framework)
4. Other README Content
  4a. Testing
  4b. Coverage
5. Other Installation Methods
6. Relevant TVB Resources
7. Acknowledgements

## 1. Additional Packages Needing Installation

For me, the following packages needed to be installed in the virtual env after installing:

      pip install llvmlite
  
For juptyer notebooks:

      pip install ipykernel

## 2. Jupyter notebook installation and tutorials

Have jupyter lab installed and do the following to allow the notebook to use the virtual env kernel:

      pip install jupyter-lab
      python -m ipykernel install --name=venv-tvb-root

## 3. Explanation of Library

### 3a. TVB Scientific library (tvb-library)

"TVB Scientific Library" is the most important scientific contribution
of TVB Project, but only a part of our code. 

"TVB Scientific Library" is a light-weight, **stand-alone** Python library
that contains all the needed packages in order to run simulations and
analysis on data without the need for the entire TVB Framework. This
implies that no storage will be provided **so data from each session will
be lost on close**. You need to either persist it yourself in some manner
or use the full TVBFramework where HDF5 / database storage is provided
as default.

   
### 3b. TVB Framework (tvb-framework)

The Virtual Brain framework is a complete framework, wrapped over tvb-library, 
and offering extra features:

-  a plug-able workflow and operations manager;
-  a data persistence layer (with a relational DB and H5 File Storage);
-  an HTML5 based user interface over CherryPy server;
-  visualizers for neuro-science related entities.
 
You can launch the **web interface** of TVB with the following command:

    python -m tvb.interfaces.web.run WEB_PROFILE tvb.config
    
Your port **8080** should be free, as a CherryPy service will try to run there.
Your default browser should automatically open <http://localhost:8080/> which is the way to
interact with TVB Web Graphical Interface.

When using from sources (Pypi or Github, not TVB_Distribution), if you want BCT adapters 
enabled, you should manually download BCT <https://sites.google.com/site/bctnet/>
and set env variable **BCT_PATH** towards the directory where you unzip BCT, plus also 
have Octave or Matlab installed with command line API enabled.

## 4. Other README Content

  ### 4a. Testing

For testing our packages, PyTest framework can be used. 

Pytest will run all files in the current directory and its subdirectories
of the form test_*.py or *_test.py.

The command for running our tests has two forms:

  1. Recommendation when working with a git clone of this TVB Github repo:
  
            cd [folder_where_tvb_framework_is]
            python -m pytest tvb/test/framework [--profile=TEST_POSTGRES_PROFILE] [--junitxml=path]
            # default profile value is TEST_SQLITE_PROFILE
    
            cd [folder_where_tvb_library_is]
            python -m pytest tvb/test/library [--junitxml=path]

  2. The second alternative form of running TVB tests, when installing TVB from Pypi, is:
        
            pip install -U tvb-framework
            python -m pytest --pyargs tvb.tests.framework
    
            pip install -U tvb-library
            python -m pytest --pyargs tvb.tests.library
    
- In order for all the tests to run correctly, the dependencies specified as LIBRARY_REQUIRED_EXTRA in [setup.py](https://github.com/the-virtual-brain/tvb-root/blob/master/scientific_library/setup.py) should be installed
- Make sure that tvb-data package is installed from [Zenodo](https://zenodo.org/record/4263723)

### 4b. Coverage

A coverage report can be generated with:

    pip install pytest-cov
    cd [folder_where_tvb_framework_is]
    py.test --cov=tvb tvb/tests/ --cov-branch --cov-report xml:[file_where_xml_will_be_generated]

    cd [folder_where_tvb_library_is]
    py.test --cov-config .coveragerc --cov=tvb tvb/tests/ --cov-branch --cov-report xml:[file_where_xml_will_be_generated]


## 5. Other Installation Methods

1. To **install** TVB code on your machine, we recommend you to first create a dedicated 
 Python env, and afterwards to take our Pypi released packages:

        pip install tvb-library
        pip install tvb-framework
   
2. Alternatively simply download **TVB_Distribution** from:
<https://www.thevirtualbrain.org/tvb/zwei/brainsimulator-software>. In this
variant, you will have Python, TVB and all our 3rd party dependencies downloaded together, 
you do not need to do anything else other than unzip and double click on **tvb_start** command.

# 6. Relevant TVB Resources

- For issue tracking we are using Jira: http://req.thevirtualbrain.org
- For API documentation and live demos, have a look here: http://docs.thevirtualbrain.org
- A public mailing list for users of The Virtual Brain can be joined and followed 
  using: tvb-users@googlegroups.com
- Raw demo IPython Notebooks can be found under: 
  https://github.com/the-virtual-brain/tvb-root/tree/master/tvb_documentation/demos
  
# 7. Acknowledgments
This project has received funding from the European Union’s Horizon 2020 Framework Programme for Research and Innovation under the Specific Grant Agreement Nos. 785907 (Human Brain Project SGA2), 945539 (Human Brain Project SGA3) and VirtualBrainCloud 826421.
