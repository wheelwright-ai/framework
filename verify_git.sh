#!/bin/bash
cd ${PROJECTS_ROOT:-~/projects}/wheelwright-ai/framework
git add -A
git status --short > git_verify_status.txt
git log -1 --oneline > git_verify_log.txt
