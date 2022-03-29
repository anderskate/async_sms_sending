# Async SMS sending service
Service for sending SMS messages asynchronously via smsc API.
Powered by Quart web framework.


# How to install
The project uses enviroment file with authorization data. The file '.env' must include following data:
- SMSC_LOGIN, login for smsc api
- SMSC_PASSWORD, passsword for smsc api
- SMSC_SENDER, sender name in smsc
- PHONES, phone numbers for sending sms
- REDIS_URL, Redis DB URL

Python 3 should be already installed. Then use pip3 (or pip) to install dependencies:

```bash
pip3 install -r requirements.txt
```

# How to launch

```bash
$ python3 server.py
```

# Project Goals

The code is written for educational purposes on online-course for web-developers dvmn.org.