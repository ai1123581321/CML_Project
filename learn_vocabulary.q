#!/bin/bash
#PBS -l walltime=08:00:00
#PBS -l nodes=1:ppn=1
#PBS -l mem=192Gb
#PBS -t 1-5
#PBS -N learn_vocabulary_job

module purge
module load python/intel/2.7.9

python ~/CML/project/CML_Project/data_processing/main.py
