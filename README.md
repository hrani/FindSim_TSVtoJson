To convert FindSim  Experiments sheet from TSV to FindSim Json format use this script

Here 4 files exist 
FindSimSchema.json : As the name sugesting its Json schema for FindSim taken from github/bhallalab/findsim
validate.py : validator to check converted Json  file against FindSimSchema
fromtsv.py : a place holder where content of FindSim TSV experiments are store
tojson.py : convert TSV to FindSim Json

To convert any FindSim TSV to Json format, run using
python tojson.py  Source Destination

Source : source file of TSV file
Destination: Destination file to write JSON


