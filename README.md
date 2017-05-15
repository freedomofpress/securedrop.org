# SecureDrop Landing Page Checker

This is a Django app that:

* Enables organizations to submit their landing page and get instant feedback on its security before submitting to Freedom of the Press Foundation
* Scans each site daily in the SecureDrop directory to grade them (credit to the Secure The News project for the scanning code)

## Developer Instructions

For initial setup, you'll need to install dependencies and apply database migrations:

```
pip3 install -r requirements.txt
python3 manage.py migrate
```

Then you can run the development server:

```
python3 manage.py runserver
```

Run tests with:

```
python3 manage.py test
```

## Deployment Instructions

Install fabric if you want to use the fabric deploy script:

```
pip3 install fabric
```

To run the deploy script, you'll need to be in the `deployment` directory. Then:

### Deploy to staging

```
fab -u ecassan deploy:host==staging.securedrop.party
```

### Deploy to prod

```
fab -u ecassan deploy:host==securedrop.party
```
