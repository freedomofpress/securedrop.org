# SecureDrop Landing Page Checker

This is a Django app enabling organizations to submit their landing page and get instant feedback on its security before submitting to Freedom of the Press Foundation.

## User Story

1. User submits landing page to form
2. User receives instant feedback: if there are issues then they are pointed to resources such that they can correct their mistakes.

## Developer Instructions

For initial setup, you'll need to install dependencies and apply database migrations:

```
pip install -r requirements.txt
python3 manage.py migrate
```

Then you can run the development server:

```
python3 manage.py runserver
```
