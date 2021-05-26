# BHM_spec_viewer
Spectral visualization tool for SDSSV-BHM

---
This is a demo for a multi-epoch spectral viewer for SDSSV-BHM using plotly/dash (https://dash.plotly.com/). 
The ultimate goal is to build a web application that allows quick spectral visualization for SDSSV BHM data. 

---
Usage:
You must have a local copy of the SDSSV data (for now). To launch the web app, you run the script as a regular python file. 
The web app will be at http://127.0.0.1:8050/, which you can open with any web browser. 

---
Here is a list of functions that people have suggested in the collaboration:
  - include previous spectra from SDSS I-IV, provide downloadable links to all data
  - include quick links to other databases (Simbad, Ned, etc...)
  - include source information summary (RA, Dec, z, source types...)
  - search with RA/Dec for objects
  - renormalization of spectra (based on specific wavelength or line)
  - smoothing of spectra 
  - show the residual spectra in greyscale (could add as a second figure)
  - optimize the loading speed, data storage, etc... 

  long term to-do list:
  - access data from Utah server (will need help from the SDSS IT team)

