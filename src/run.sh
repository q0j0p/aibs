#! /usr/bin/env bash

python src/pipeline.py GetZippedSwc --species drosophila\ melanogaster --local-scheduler --workers 5
python src/pipeline.py GetZippedSwc --species drosophila\ melanogaster
