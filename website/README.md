# Click2hedge — Website

This is a minimal static website scaffold for Click2hedge Financial Planner.

How to view locally:

1. Open `website/index.html` in your browser.
2. Or serve with Python HTTP server from the `website` folder:

```powershell
cd website
python -m http.server 8000
# then open http://localhost:8000
```

Files:
- `index.html` — single-page site
- `styles.css` — styling
- `script.js` — contact form and small behaviors

Next steps:
- Hook contact form to a backend or form provider (Formspree, Netlify Forms, or your API). The current form uses `mailto` as a fallback.
- Replace the placeholder logo at `website/assets/logo.svg` with your brand asset.
- Add SEO/meta tags and analytics as needed.

Module pages:
- `onboarding.html` — client onboarding details
- `financial_plan.html` — financial plan offering
- `itr_filing.html` — ITR filing process
- `portfolio_monitoring.html` — portfolio monitoring

