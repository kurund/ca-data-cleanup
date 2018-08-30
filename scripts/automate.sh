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
cd ../careeraware/
echo 'Identify batches to process.'
python manage.py shell < scripts/import_sf.py

DIR=to-process

# check for batches to process
if [ "$(ls -A $DIR)" ]; then
     echo 'Batches are ready for processing.'
else
    echo "No batches to process."
    exit
fi

# start processing of batches
cd $DIR

for d in */ ; do
    # copy files to dataloader data folder for processing
    echo ''
    echo "-----------------------------------------------"
    echo "Processing: $d"
    cp -R $d*.csv ../../dataloader/data/

    # call data loader to push data to SF
    pushd ../../dataloader/ > /dev/null

    bin/process.sh Baseline1
    echo "Baseline 1 done."
    bin/process.sh Baseline2
    echo "Baseline 2 done."
    bin/process.sh CareerAwareness
    echo "Career Awareness done."
    bin/process.sh CareerPlanning
    echo "Career Planning done."
    bin/process.sh SelfAwareness
    echo "Self Awareness done."
    bin/process.sh CounsellingAndFeedback
    echo "Counselling and Feedback done."

    popd > /dev/null

    # delete processed files from data loader data folder
    echo "Delete processed files from dataloader."
    rm -rf ../../dataloader/data/*.csv

    # delete processed files from to-process folder
    echo "Delete batch from process queue."
    rm -rf $d
    echo "-----------------------------------------------"
done