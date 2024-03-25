# Run it with `./tools/build.sh`
# from icclim root
# and with "icclim-dev" conda environment activated
pip install .
python ./tools/extract-icclim-funs.py
git add ./src/icclim/_generated/
pre-commit run
