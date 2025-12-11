# Fixing FUNCTION_INVOCATION_FAILED on Vercel

## The Error
`500: INTERNAL_SERVER_ERROR` with `FUNCTION_INVOCATION_FAILED`

This means the serverless function is crashing at runtime, not during build.

## Most Likely Causes

1. **Data loading is too slow or timing out**
   - Loading 12,000+ restaurants takes time
   - Serverless functions have cold start limits

2. **File path issues**
   - Vercel runs from a different directory structure
   - File paths need to be absolute

3. **Import errors**
   - Dependencies not installed correctly
   - Circular imports

## What I've Fixed

1. ✅ Added error handling in `api/index.py`
2. ✅ Fixed file paths in `app.py` to use absolute paths
3. ✅ Added try/except around data loading
4. ✅ Error handler will show actual error messages

## Next Steps

### Step 1: Check Vercel Function Logs

**IMPORTANT:** The error handler I added will show the actual error on your site!

1. Go to your Vercel deployment URL
2. You should now see a detailed error page (instead of generic 500)
3. This will tell us exactly what's failing

**OR** check Vercel dashboard:
- Go to your project
- Click "Functions" tab
- Click on `api/index.py`
- View "Logs" to see runtime errors

### Step 2: Common Fixes

**If you see "File not found: processed_data.json":**
```bash
# Make sure it's committed
git add processed_data.json
git commit -m "Ensure processed_data.json is tracked"
git push
```

**If you see import errors:**
- Check `requirements.txt` has all packages
- Verify build logs show packages installing

**If you see timeout errors:**
- The JSON file (8.5 MB) might be too slow to load
- We may need to optimize data loading (lazy load)

### Step 3: Commit and Push

```bash
git add .
git commit -m "Improve Vercel error handling - show actual errors"
git push
```

## After Pushing

1. Visit your Vercel URL
2. If it still fails, you'll now see the **actual error message**
3. Share that error message with me so I can fix it!

The error page will show exactly what's wrong instead of just "500 error".

