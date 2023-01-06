
# Website tracking site 


# Getting Started
These instructions will get you a running on your local machine for development .

## Prerequisites
make sure edit .env file and add your database information

## Installation

A step by step guide on how to set up the project on your local machine.

### Clone the repository

```bash
git clone https://github.com/Paresh-Maheshwari/website_tracker.git
```

```bash
  pip install virtualenv
```
    


 Run virtualenv in your machine

```bash
 
# macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python3 -m venv .venv
.venv\scripts\activate
```
    

## Install Requirment 
```bash
pip install -r requirements.txt
```
## Update a database

```bash
python manage.py migrate
```

## Make new superuser 
python manage.py createsuperuse

## Run server
```bash
python manage.py runserver 0.0.0.0:8000
```

## Install in Linux  System

```bash
bash  install.sh
```



