# Deploying to Vercel

## Important Setup Steps

### 1. Convert Excel Data to JSON

Before deploying to Vercel, you must convert your Excel data to JSON format:

```bash
python convert_to_json.py
```

This will create `processed_data.json` which will be used on Vercel (Excel files don't work well in serverless environments).

### 2. Commit the JSON File

The `processed_data.json` file should be committed to Git (it's not in .gitignore):

```bash
git add processed_data.json
git commit -m "Add processed restaurant data JSON for Vercel deployment"
git push
```

### 3. Deploy to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Import your GitHub repository: `julanraveendran/Londonfoodfindsuk`
3. Vercel will auto-detect Python and use the configuration from `vercel.json`
4. Deploy!

## File Structure for Vercel

```
/
├── api/
│   └── index.py          # Serverless function entry point
├── templates/            # HTML templates
├── static/               # CSS and JS files
├── app.py                # Flask application
├── processed_data.json   # Processed restaurant data (required!)
├── vercel.json           # Vercel configuration
└── requirements.txt      # Python dependencies
```

## Troubleshooting

### Error: "Function invocation failed"
- Make sure `processed_data.json` exists and is committed to Git
- Check that all dependencies in `requirements.txt` are compatible with Vercel

### Error: "Module not found"
- Ensure `requirements.txt` includes all dependencies
- Vercel installs packages automatically from `requirements.txt`

### Data not loading
- Verify `processed_data.json` is in the root directory
- Check Vercel build logs for any errors during data loading

## Updating Data

When you need to update restaurant data:

1. Update the Excel file locally
2. Run: `python convert_to_json.py`
3. Commit and push the updated `processed_data.json`
4. Vercel will automatically redeploy

