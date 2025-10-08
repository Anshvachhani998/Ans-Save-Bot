
#!/bin/bash

# Folder Name
DIR="Ans-Save-Bot"

# GitHub Personal Access Token (PAT)

# GitHub repo info
GITHUB_USER="Anshvachhani998"
GITHUB_REPO="Ans-Save-Bot"

# Check if the folder exists
if [ -d "$DIR" ]; then
    echo "📂 $DIR found. Entering directory..."
    cd $DIR || exit 1
else
    echo "❌ $DIR not found! Running commands in the current directory..."
fi

# Pull the latest updates using PAT
echo "🔄 Updating repository..."
git pull https://github.com/$GITHUB_USER/$GITHUB_REPO.git

# Restart Docker Container
echo "🚀 Restarting SpotifyDL Docker container..."
docker restart Ans-Save-Bot

echo "✅ Update & Restart Completed!"
