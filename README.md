## About This Project

This project was completed by **Jacob S** for the **AC0 Software Engineering & Agile QA** module.

## Setup

To start, run the following commands in your terminal:

```bash
pip install -r requirements.txt
python setup_db.py
flask --debug run
```

### Sample Data

All user accounts in the sample data use the password **password**.

### Alerts

All alert messages appear at the bottom of the screen to provide useful success and failure prompts.

### Additional Information

This application is an **IT Asset Management Tool** developed for Marks & Spencer.

- Any user can create a new asset and assign it to themselves and any department.
- Users can edit or delete their own user accounts.
- Created assets are initially in a pending state (_Approved = No_), visible on the assets table and dashboard, waiting for admin approval.
- Users can only see their own assets and their own user account in the users table.

### Admin Capabilities

Admins have increased privileges including:

- Approving assets.
- Creating and assigning assets to any user.
- Promoting users to admin.
- Performing create, read, update, and delete (CRUD) operations on Assets, Departments, and Users.
