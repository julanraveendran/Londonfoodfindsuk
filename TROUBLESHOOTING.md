# Vercel Deployment Troubleshooting

## Common Errors and Solutions

### Error: "Function invocation failed" or 500 Internal Server Error

**Possible Causes:**
1. Missing `processed_data.json` file
2. Import errors
3. Path issues
4. Data loading timeout

**Solutions:**

#### 1. Ensure processed_data.json is committed
```bash
# Check if file exists locally
ls -lh processed_data.json

# If missing, regenerate it
python convert_to_json.py

# Add to git (if not already)
git add processed_data.json
git commit -m "Add processed_data.json"
git push
```

#### 2. Check Vercel Build Logs
- Go to your Vercel dashboard
- Click on your deployment
- Check "Build Logs" tab for Python errors
- Look for import errors or file not found errors

#### 3. Verify File Structure
Your repository should have:
```
/
├── api/
│   └── index.py          ✅
├── app.py                ✅
├── processed_data.json   ✅ (must be committed!)
├── vercel.json           ✅
├── requirements.txt      ✅
├── templates/            ✅
└── static/               ✅
```

### Error: "Module not found"

**Solution:**
- Check `requirements.txt` includes all dependencies:
  ```
  Flask>=3.0.0
  pandas>=2.2.0
  openpyxl>=3.1.2
  werkzeug>=3.0.0
  ```
- Vercel installs from requirements.txt automatically

### Error: "File not found: processed_data.json"

**Causes:**
- File not committed to Git
- File too large for Git (unlikely, but possible)
- Path issues on Vercel

**Solution:**
```bash
# Check if file is tracked by git
git ls-files | grep processed_data.json

# If empty, add it
git add processed_data.json
git commit -m "Add processed data"
git push
```

### Error: "Timeout" or "Function timeout"

**Cause:** Data loading takes too long

**Solution:**
- The JSON file loads much faster than Excel
- If still timing out, check JSON file size (should be ~8-9 MB)
- Consider optimizing data structure if needed

### Error: Import Error in api/index.py

**Check:**
- Ensure `app.py` is in the root directory
- Verify `sys.path` is correct in `api/index.py`
- Check build logs for specific import errors

## Debugging Steps

1. **Check Build Logs:**
   ```
   Vercel Dashboard → Your Project → Deployment → Build Logs
   ```

2. **Test Locally First:**
   ```bash
   # Make sure it works locally
   python app.py
   # Visit http://localhost:5000
   ```

3. **Verify Files are Committed:**
   ```bash
   git status
   git log --name-only --oneline -1
   ```

4. **Check File Sizes:**
   - `processed_data.json` should be ~8-9 MB
   - Too large? Git might reject it (GitHub limit is 100MB)

## Still Having Issues?

1. Check Vercel Function Logs (not just build logs)
2. Try deploying a minimal test first
3. Ensure Python version compatibility
4. Check Vercel's Python runtime documentation

## Quick Fix Checklist

- [ ] `processed_data.json` exists and is committed
- [ ] `api/index.py` exists
- [ ] `vercel.json` is configured correctly
- [ ] `requirements.txt` has all dependencies
- [ ] All templates and static files are committed
- [ ] Build logs show no errors
- [ ] Function logs (runtime) show no errors

