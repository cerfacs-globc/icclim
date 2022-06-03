# Run it with `./tools/build.sh`
# from icclim root
# and with "icclim-dev" conda environment activated
python -m setup install
python ./tools/extract-icclim-funs.py ./icclim/_generated_api.py
git add ./icclim/_generated_api.py
pre-commit run
