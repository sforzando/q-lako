# q-lako

[![On push](https://github.com/sforzando/q-lako/workflows/On%20push/badge.svg)](https://github.com/sforzando/q-lako/actions?query=workflow%3A%22On+push%22)
[![CodeQL](https://github.com/sforzando/q-lako/workflows/CodeQL/badge.svg)](https://github.com/sforzando/q-lako/actions?query=workflow%3ACodeQL)
[![codecov](https://codecov.io/gh/yusuke-sforzando/q-lako/branch/main/graph/badge.svg?token=aDS6wgB3Hn)](https://codecov.io/gh/yusuke-sforzando/q-lako)

![logo](https://user-images.githubusercontent.com/32637762/97838815-53fc3d80-1d24-11eb-8668-58037a4a61a7.png)

q-lako is a service to quickly register equipments and books.
q-lako is a web app that helps you to manage books and supplies purchased on Amazon.

- [Retrievable information](#retrievable-information)
- [Requirements](#requirements)
- [How to](#how-to)
  - [Enter Python Virtual Environment](#enter-python-virtual-environment)
  - [Prepare `.env` and `.env.gpg`](#prepare-env-and-envgpg)
  - [Prepare `settings.ini`](#prepare-settingsini)
  - [Run](#run)
  - [Lint](#lint)
  - [Test](#test)
- [Misc](#misc)
  - [Contributor](#contributor)

## Retrievable information

Get the following information on purchased books and supplies to help you register supplies.

- Product Title
- ASIN Code
- Image (url)
- URL
- Manufacturer
- Contributors
- Publication Date
- Product Group
- Registrants Name
- Default Positions
- Current Positions
- Note
- Features

## Requirements

- [Python](https://www.python.jp) 3.8.4 or higher
  - [Flask](https://flask.palletsprojects.com/)
- [Google Cloud Platform](https://console.cloud.google.com/)
  - [Google App Engine](https://cloud.google.com/appengine)
- [GnuPG](https://gnupg.org)

## How to

### Enter Python Virtual Environment

```shell
python3 -m venv venv
source venv/bin/activate
export ARCHFLAGS="-arch x86_64"
pip install --upgrade pip
pip install --upgrade --use-feature=2020-resolver -r requirements.txt
```

The reason why `ARCHFLAGS` needs to be specified is due to [Apple's bugs in Xcode12](https://github.com/giampaolo/psutil/issues/1832).
It is recommended to explicitly specify the resolver options until [`pip` version 20.3](https://www.python.jp/pages/2020-10-07-new-pip-deps.html#%E6%96%B0%E3%81%97%E3%81%84%E4%BE%9D%E5%AD%98%E3%83%AA%E3%82%BE%E3%83%AB%E3%83%90).

### Prepare `.env` and `.env.gpg`

Write the API Key to `.env` and encrypt it.
Keep your passphrase in a secure location like [YubiKey](https://www.yubico.com).

1. Prepare `.env`

    ```.env
    airtable_base_id="airtable_base_id"
    airtable_api_key="airtable_api_key"
    amazon_partner_tag="amazon_partner_tag"
    amazon_access_key="amazon_access_key"
    amazon_secret_key="amazon_secret_key"
    ```

1. Encrypt `.env` to create `.env.gpg`

    `gpg --symmetric --cipher-algo AES256 .env`

1. Use your passphrase to decrypt `.env.gpg` .

    `gpg --quiet --batch --decrypt --output=.env .env.gpg`

### Prepare `settings.ini`

```settings.ini
[THEME-COLOR]
theme_color_blue=#4caaba
theme_color_gray=#393e46

[AIRTABLE]
airtable_table_name=q-lako
```

### Run

```shell
python main.py
```

If you start it locally, it will start in **Debug** mode.

1. Access to `http://0.0.0.0:8888/`
1. Enter keywords or ISBN/ASIN code in the search window and press the search button
1. Displays a list of items related to the keywords you have entered
1. Select any item from the list of items and press the Select button
1. The item's details are displayed
1. Edit the contents of the item's details form
1. Press the Register button and you will be registered with Airtable

### Lint

```shell
flake8 *.py
```

### Test

```shell
pytest . -vv --ignore-glob="venv/**/*" --durations=0
```

## Misc

### Contributor

- Chief Engineer: [Yusuke Watanabe](https://github.com/yusuke-sforzando)
- Product Manager: [Tomoya Kashimada](https://github.com/tomoya-sforzando)
- Business Owner: [Shin'ichiro Suzuki](https://github.com/shin-sforzando)
