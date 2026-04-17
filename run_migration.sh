#!/bin/bash
cd ${PROJECTS_ROOT:-~/projects}/wheelwright-ai/framework
python3 migrate_scf_to_wheelwright.py "$@"
