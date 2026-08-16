Demo backend to store enquiries in a local SQLite database.

Run locally:

```powershell
python -m pip install -r backend/requirements.txt
python backend/app.py
```

API endpoints:
- `POST /api/submit_enquiry` JSON {name,email,phone,message}
- `GET  /api/enquiries` returns saved enquiries

This is a demo service; for production use a proper DB, auth and rate-limiting.
