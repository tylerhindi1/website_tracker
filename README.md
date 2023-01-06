
# TrackMySite
This project allows users to track their location when visiting a website and view their location data in a dashboard. They can also export their location data in CSV, JSON, or Excel format. Additionally, users can send a message to the website administrator through a contact form, and the administrator can receive notifications about new contact form submissions and user location data via Telegram. The project also includes a password reset feature to allow users to reset their password if they forget it.

## Prerequisites
- Python 3.8 or later
- Django 3.9 or later
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`BOT_TOKEN`

`CHAT_ID`

`SERVER_ADDRESS`

`SECRET_KEY`

`EMAIL_HOST_USER`

`EMAIL_HOST_PASSWORD`
# Installation

### Clone the repository

```bash
 git clone https://github.com/Paresh-Maheshwari/website_tracker.git
 cd website_tracker
```
## Windows Installation



```bash
 pip install virtualenv
```
    


 Run virtualenv in your machine

```bash
 python3 -m venv .venv
 .venv\scripts\activate
```
    

### Install Requirment 
```bash
pip install -r requirements.txt
```
### Update a database

```bash
python manage.py migrate
```

### Make new superuser 
```bash
python manage.py createsuperuse
```

### Run server
```bash
python manage.py runserver 0.0.0.0:8000
```

## Install in Linux  System

```bash
bash  install.sh
```

## Features


- User Registration: Users can create a new account by providing their email, password, and other personal details. The email address will be used to send a verification link, which the user must click to verify their email and complete the registration process.

- User Login: Once registered, users can log in to their account using their email and password. If the email and password are correct, the user will be logged in and redirected to the home page.

- Password reset: Users can reset their password if they have forgotten it.


- Notification: User can update a own chat_it  to receive a all usertracking data in telegram bot

- Admin panel built using Django-Jazzmin library: Allows the website administrator to manage users, view location data, and access other administrative functions.

- Telegram integration:  The website can receive notifications about new  user location data via Telegram. Users can also update their own Telegram chat ID to receive their location data.

- Unique tracking code: Users can use a unique tracking code to track their location on the website and receive updates about their location data via Telegram.
- User dashboard:  Users can view their location data, including the date and time of each visit, their IP address, and a map showing their location. They can also see their daily, monthly, yearly, and total visit count.

- Export data:Users can export their location data as a CSV, JSON, or Excel file by clicking the "Export Data" button on the location track page. This allows users to save their location data for offline use or to import it into another 

- Tracking User Location: The project tracks the location of users who visit the website. When a user visits the website, their location data (e.g., IP address, latitude, longitude, etc.) is stored in a database. This data can be accessed by the user through the "User Track" page.



- Contact Form: The project includes a contact form that allows users to send messages to the administrator. The form collects the user's name, email, and message, and sends them to the administrator via email or Telegram.
## Contributing

Contributions are welcome and greatly appreciated. To contribute to the project, please follow these steps:
- Fork the repository.
- Create a new branch for your feature or bug fix.
- Commit your changes and push to the new branch.
- Create a pull request.
## Authors

- [@Paresh-Maheshwari](https://github.com/Paresh-Maheshwari)


## License

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License 
