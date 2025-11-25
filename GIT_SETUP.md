# Git Setup and Push Instructions

## Step 1: Install Git

If Git is not installed on your system:

1. **Download Git for Windows**: https://git-scm.com/download/win
2. Install it with default settings
3. Restart your terminal/PowerShell after installation

## Step 2: Configure Git (if first time)

Open PowerShell or Command Prompt and run:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Initialize and Push to GitHub

Once Git is installed, run these commands in your project directory:

```bash
# Navigate to your project directory
cd C:\Users\julan\Downloads\londonfoodfindsuk

# Initialize git repository
git init

# Add all files (except those in .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: London Food Finds UK directory website"

# Add the remote repository
git remote add origin https://github.com/julanraveendran/Londonfoodfindsuk.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Alternative: Using GitHub Desktop

If you prefer a GUI:

1. Download GitHub Desktop: https://desktop.github.com/
2. Sign in with your GitHub account
3. Click "Add" → "Add Existing Repository"
4. Select your project folder
5. Commit and push through the interface

## Note

The Excel file `OS-20251124200014m1e_restaurant.xlsx` is in `.gitignore` because:
- It's very large (56,875 lines)
- GitHub has file size limits
- It should be kept locally or uploaded separately to cloud storage

If you need to track the Excel file separately, consider:
- Using Git LFS (Large File Storage)
- Uploading it to a cloud storage service
- Sharing it privately with collaborators


