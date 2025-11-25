# Quick Fix for Vercel Deployment

## The Problem
Vercel was giving a 500 error because:
1. The Excel file is too large and not included in Git
2. Flask apps need proper serverless function setup for Vercel

## The Solution
I've created all necessary files for Vercel deployment:

### Files Created:
- ✅ `api/index.py` - Vercel serverless function entry point
- ✅ `vercel.json` - Vercel configuration
- ✅ `processed_data.json` - Pre-processed restaurant data (8.5 MB)
- ✅ `convert_to_json.py` - Script to regenerate JSON from Excel

### Next Steps:

1. **Commit and push all new files:**
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration and processed data"
   git push
   ```

2. **Redeploy on Vercel:**
   - Go to your Vercel dashboard
   - Click "Redeploy" on your latest deployment
   - Or push a new commit to trigger automatic deployment

## What Changed:

1. **Data Loading**: The app now loads from `processed_data.json` instead of Excel (faster for serverless)
2. **Serverless Function**: Created `api/index.py` as the entry point Vercel expects
3. **Configuration**: Added `vercel.json` to route all requests properly

## File Structure:
```
/
├── api/
│   └── index.py          ← Vercel serverless function
├── app.py                ← Your Flask app
├── processed_data.json   ← Restaurant data (needed for Vercel!)
├── vercel.json           ← Vercel config
└── ... (other files)
```

The deployment should work now! 🎉

