# Restaurant Award Badge Setup Guide

## Overview
This guide explains how to distribute the "Best Restaurant Award" badge to restaurant owners so they can display it on their websites with a backlink to https://londonfoodfindsuk.co.uk/

## Image Location
- **File**: `static/images/best-restaurant-award.png`
- **Live URL**: `https://londonfoodfindsuk.co.uk/static/images/best-restaurant-award.png`
- **Status**: ✅ Image is uploaded and accessible

## Files for Restaurant Owners

### 1. HTML Code File
**File**: `RESTAURANT_BADGE_CODE.html`
- Contains the HTML code snippet that restaurant owners can copy and paste
- Includes clear instructions
- Ready to send or include in emails

### 2. Email Template
**File**: `RESTAURANT_BADGE_EMAIL.txt`
- Professional email template ready to send to restaurant owners
- Includes instructions and the HTML code
- Just replace `[Restaurant Owner Name]` with the actual name

## HTML Code (What Restaurants Will Use)

```html
<a href="https://londonfoodfindsuk.co.uk/" target="_blank" rel="nofollow noopener" title="London Food Finds UK - Best Restaurant Award">
  <img src="https://londonfoodfindsuk.co.uk/static/images/best-restaurant-award.png" 
       alt="Best Restaurant Award - London Food Finds UK" 
       style="max-width: 200px; height: auto; display: block;">
</a>
```

## Key Features of the Code

1. **Backlink**: Links to `https://londonfoodfindsuk.co.uk/`
2. **Opens in New Tab**: `target="_blank"` ensures visitors stay on the restaurant's site
3. **SEO-Friendly**: Includes `rel="nofollow noopener"` and proper alt text
4. **Responsive**: `max-width` ensures it scales on mobile devices
5. **Customizable**: Easy to change the size by adjusting the `max-width` value

## How to Use

### Option 1: Send via Email
1. Open `RESTAURANT_BADGE_EMAIL.txt`
2. Replace `[Restaurant Owner Name]` with the actual restaurant owner's name
3. Copy and send the email

### Option 2: Send HTML Code Directly
1. Open `RESTAURANT_BADGE_CODE.html`
2. Copy the HTML code (excluding the comment instructions if desired)
3. Paste it into your email or communication tool

### Option 3: Create a Page on Your Site
- Create a page like `/award-badge` that explains the badge program
- Include the HTML code on that page for restaurants to copy
- Share the page URL with restaurant owners

## Verification

After restaurants add the badge, you can verify:
1. The image loads correctly: Check that `https://londonfoodfindsuk.co.uk/static/images/best-restaurant-award.png` is accessible
2. The link works: Click the badge to ensure it links to your homepage
3. Backlink tracking: Use tools like Google Search Console to monitor backlinks

## Troubleshooting

### Image Not Showing
- Verify the image URL is correct: `https://londonfoodfindsuk.co.uk/static/images/best-restaurant-award.png`
- Check that the image file exists in `static/images/`
- Clear browser cache

### Link Not Working
- Ensure the link points to: `https://londonfoodfindsuk.co.uk/`
- Check that the website is live and accessible

## Size Customization Examples

```html
<!-- Small Badge (150px) -->
<img src="..." style="max-width: 150px; height: auto; display: block;">

<!-- Medium Badge (200px) - Default -->
<img src="..." style="max-width: 200px; height: auto; display: block;">

<!-- Large Badge (300px) -->
<img src="..." style="max-width: 300px; height: auto; display: block;">
```

## Next Steps

1. ✅ Image is uploaded and accessible
2. ✅ HTML code is ready
3. ✅ Email template is prepared
4. 📧 Start sending the badge code to restaurant owners
5. 📊 Track backlinks using Google Search Console or other SEO tools

