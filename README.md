[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/cms-outreach/ispy-nanoaod/HEAD) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/cms-outreach/ispy-nanoaod/blob/master/examples/load_event_and_display.ipynb) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17369554.svg)](https://doi.org/10.5281/zenodo.17369554)

# iSpy NanoAOD: An event display for the CMS NanoAOD format

This application allows one to visualize events in the CMS NanoAOD format in a Jupyter notebook.

## Installation
```
pip install ispynanoaod
```

### Installation for developers:
Clone this repository:
```
git clone https://github.com/cms-outreach/ispy-nanoaod.git
```
Install locally:
```
cd ispy-nanoaod
pip install -e .
```

## Usage
See the example notebooks in the `examples` dir. You may also open and run them
using the link to Binder above.

### Quick start
Open a notebook using for example `jupyter lab`.

Import the libraries:
```
import os
import subprocess
import ispynanoaod as ispy
```

Download some data:
```
file_name = 'EEB2FE3F-7CF3-BF4A-9F70-3F89FACE698E.root'
file_url = 'http://opendata.cern.ch/eos/opendata/cms/Run2016H/DoubleMuon/NANOAOD/UL2016_MiniAODv2_NanoAODv9-v1/2510000/EEB2FE3F-7CF3-BF4A-9F70-3F89FACE698E.root'

if not (os.path.isfile(f'{file_name}')):
    subprocess.run(['curl', '-O', f'{file_url}'])
```

Visualize:
```
display = ispy.EventDisplay()
display.load_file(file_name)
display.display()
```

![image](imgs/ispynanoaod-quickstart.png)




