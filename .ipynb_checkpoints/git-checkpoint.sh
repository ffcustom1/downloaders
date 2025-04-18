#!/bin/bash

# GitHub credentials (update with your actual username and token)
GITHUB_USER="ffcustom1"
GITHUB_TOKEN="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"
REPO_NAME="downloaders"
BRANCH="main"

# Set the remote URL (only needs to be done once, but it's safe to keep)
git remote set-url origin https://$GITHUB_USER:$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git

# Add specific files and folders
git add *.txt *.sh *.log *.py extra/ 2>/dev/null

# Commit with the current date
DATE=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "Auto commit on $DATE"

# Push to GitHub
git push origin $BRANCH
