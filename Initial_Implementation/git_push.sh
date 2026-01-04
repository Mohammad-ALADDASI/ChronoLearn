#!/bin/bash

# ---------------------------------------
# Auto Git Push Script for the ENR Project
# ---------------------------------------

echo "🔍 Checking for Git repository..."
if [ ! -d ".git" ]; then
    echo "❌ No Git repository found. Run: git init"
    exit 1
fi

echo "🔧 Adding all changes..."
git add .

echo "📝 Enter commit message (leave empty for default):"
read msg

if [ -z "$msg" ]; then
    msg="Auto-update"
fi

echo "💬 Committing..."
git commit -m "$msg"

echo "🚀 Pushing to GitHub..."
git push

echo "✅ Done!"
