#!/bin/bash
cd /home/mario/projects/wheelwright-ai/framework
git add -A
git status --short > git_verify_status.txt
git log -1 --oneline > git_verify_log.txt
