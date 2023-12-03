#! /usr/bin/env bash

# first prompt for the branch name
read -r -p "Enter the new branch name: " branch_name


git checkout dev
git pull
git checkout main
git pull
git checkout -b "$branch_name"
git checkout dev -- static/vars.py django_project/settings.py
git restore --staged static/vars.py django_project/settings.py
git push -u origin "$branch_name"
