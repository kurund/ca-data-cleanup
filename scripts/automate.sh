#!/usr/bin/env bash
# This script automates the process of pushing CSV data to SF for Career Aware project
# Basic overview
#   1. Python script
#	    * From the DB pick up batches with pending status
#	    * Copy the files that needs to be processed to to-process folder
#
#   2. Bash logic
#	    * Iterate to-process folder
#		    * Picks data from to-process folder and copies it to respective folder
#		    * Runs the data loader script
#		    * Delete copied files from data loader
#		    * Delete files from to-process folder

# python script related actions
source ../env/bin/activate
echo 'Virtual environment activated.'
cd ../careeraware/
echo 'Run python script to identify batches to process.'
python manage.py shell < scripts/import_sf.py
echo 'Batches are ready for processing.'

# start processing of batches

