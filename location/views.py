from audioop import reverse
import json
import os
import requests
from django.http import HttpResponse
from django.shortcuts import redirect
import secrets
from django.shortcuts import render
from .forms import UserCreateForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from datetime import  datetime
from .forms import *
from .models import *
import xlwt
import pytz
import csv
from django.utils import timezone
from django.core.mail import EmailMessage



def home(request):
    return render(request,'home.html')

#######################  Login  start   ############################
@login_required
def logoutaccount(request):
    logout(request)
    return redirect('home')


def login_view(request):
    if request.method == 'GET':
        return render(request, 'registration/login.html',{'form':AuthenticationForm})

    # Get the email and password from the form
    email = request.POST['email']
    password = request.POST['password']

    try:
        # Look up the user by email
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # If the user does not exist, display an error message
        return render(request, 'registration/login.html', {'form': AuthenticationForm(), 'error': 'The email is not registered. Please sign up.'})

    if not user.is_active:
        return render(request, 'registration/login.html', {'form': AuthenticationForm(), 'error': 'Your email is not verified. Please check your email and follow the verification link.'})

# Authenticate the user using their email and password
    user = authenticate(request, username=user.username, password=password)

    if user is None:
        return render(request, 'registration/login.html', {'form': AuthenticationForm(), 'error': 'email and password do not match'})

    login(request, user)
    return redirect('home')
#######################  Login  stop   ############################

#######################  Register start ############################
@receiver(models.signals.pre_save, sender=TokenSummary)
def generate_link(sender, instance, **kwargs):
    # Get the server address from the environment variable
    server_address = os.environ.get("SERVER_ADDRESS")

    # If the server address is not set, use a default value
    if not server_address:
        server_address = "localhost"

    token = instance.token
    slug = slugify(token)
    link = f"{server_address}/location/{slug}"
    instance.link = link

def send_verification_email(request, user):
    # Generate a random verification code
    verification_code = secrets.token_hex(16)
    
    # Save the verification code to the database
    VerificationCode.objects.create(
        user=user,
        code=verification_code,
        expires_at=timezone.now() + timezone.timedelta(hours=24)
    )
    server_address = os.environ.get("SERVER_ADDRESS")
    # Construct the verification email message
    subject = 'Email Verification'
    message = f"Your verification code is: {server_address}/verify/{verification_code}"
    recipient_list = [user.email]
    from_email='noreply@example.com'
    
    # Create an EmailMessage object
    email = EmailMessage(subject, message, from_email, recipient_list)
    
    # Send the email
    email.send()

def verify(request, code):
    # Look up the verification code in the database
    try:
        ver_code = VerificationCode.objects.get(code=code)
    except VerificationCode.DoesNotExist:
        # If the code is invalid, display an error message
        return render(request, 'registration/verify.html', {'error': 'Invalid verification code'})

    # Check if the verification code has expired
    if timezone.now() > ver_code.expires_at:
        # If the code has expired, display an error message
        return render(request, 'registration/verify.html', {'error': 'Verification code has expired'})

    # Activate the user's account
    user = ver_code.user
    user.is_active = True
    user.save()

    #after verification delete the code
    ver_code.delete()
    
    # Display a success message
    return render(request, 'registration/verify.html', {'success': 'Your account has been verified'}) 
    


def register(request):  
    if request.method == "GET":
        return render(request, "registration/register.html", {"form": UserCreateForm})

    if request.POST["password1"] != request.POST["password2"]:
        # If the passwords do not match, display an error message
        return render(
            request,
            "registration/register.html", 
            {"form": UserCreateForm, "error": "Passwords do not match"},
        )

    # Check if the provided email already exists in the database
    if User.objects.filter(email=request.POST["email"]).exists():
        # If the email already exists, display an error message
        return render(
            request,
            "registration/register.html",
            {"form": UserCreateForm, "error": "Email already taken. Choose new email."},
        )

    try:
        # Create a new user using the provided email, username, and password
        author = User.objects.create_user(
            username=request.POST["username"],
            email=request.POST["email"], 
            password=request.POST["password1"]
        )
        # Set the user's is_active field to False to prevent login until the email is verified
        author.is_active = False
        author.save()

        # Generate a random token with 64 characters
        token = secrets.token_hex(8)

        # Check if the token already exists in the database
        if TokenSummary.objects.filter(token=token).exists():
            # If the token already exists, generate a new token
            token = secrets.token_hex(8)
    
        # Create a new TokenSummary object using the form data
        token_summary = TokenSummary.objects.create(
            author=author, token=token
        )

        # Generate the unique link for the user using the generate_link function
        generate_link(sender=TokenSummary, instance=token_summary) 
        # Send the email verification code
        send_verification_email(request, author)
        
        # Display a message indicating that the email has been sent
        return render(
            request,
            "registration/register.html",
            {"form": UserCreateForm, "success": "Verification email sent. Please check your email."},
        )
    except Exception as e:
        # If there was an error creating the user, display an error message
        return render(
            request,
            "registration/register.html",
            {"form": UserCreateForm, "error": str(e)},
        )
#########################  Register end  ##############################


###################### Reset Password start  ##########################
def send_reset_email(request, user):
    # Generate a random reset code
    reset_code = secrets.token_hex(16)
    
    # Save the reset code to the database
    ResetCode.objects.create(
        user=user,
        code=reset_code,
        expires_at=timezone.now() + timezone.timedelta(hours=24)
    )
    server_address = os.environ.get("SERVER_ADDRESS")
    # Construct the reset email message
    subject = 'Password Reset'
    message = f"To reset your password, follow this link: {server_address}/reset/{reset_code}"
    
    recipient_list = [user.email]
    from_email='noreply@example.com'
    # Create an EmailMessage object
    email = EmailMessage(subject, message, from_email,recipient_list)
    
    # Send the email
    email.send()

from django.contrib.auth import get_user_model

def forgot_password(request):
    #check if the request is a GET or POST
    if request.method == 'GET':
        return render(request, 'registration/forgot_password.html')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            UserModel = get_user_model()
            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                user = None
            if user is not None:
                send_reset_email(request, user)
                return render(request, 'registration/forgot_password_done.html')
    else:
        form = ForgotPasswordForm()
    return render(request, 'registration/forgot_password.html', {'error': 'The email is not registered. Please sign up.'})

def reset_password(request, reset_code):
    # Get the reset code from the database
    try:
        reset_code_obj = ResetCode.objects.get(code=reset_code)
    except ResetCode.DoesNotExist:
        # Return an error if the reset code is not found
        return render(request, 'registration/reset_password_invalid.html')
    
    # Check if the reset code is expired
    if timezone.now() > reset_code_obj.expires_at:
        # If the code has expired, display an error message
        return render(request, 'registration/reset_password_invalid.html', {'error': 'This token is expired. Click here to resend.'})
    
    # The reset code is valid, so allow the user to reset their password
    if request.method == 'POST':
        # Process the form data to reset the password
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            # Update the user's password
            user = reset_code_obj.user
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Delete the reset code from the database
            reset_code_obj.delete()
            
            # Redirect to the password reset successful page
            return render(request, 'registration/reset_password_done.html')
    else:
        # Display the password reset form
        form = ResetPasswordForm()
    return render(request, 'registration/reset_password.html', {'form': form})

########################## Reset Password end  ##################################

##################### User track and send data start  ###########################    
@login_required
def user_track(request):
    # Get the visit count, today's total, monthly total, and yearly total for the authenticated user
    visit, created = VisitCount.objects.get_or_create(author=request.user)
    visit_count = visit.visit_count
    today_total = visit.today_total
    monthly_total = visit.monthly_total
    yearly_total = visit.yearly_total
    # data is display to deseding order
    
    userdata = UserLocation.objects.order_by('-date','-time')[:100]   

    if request.user.is_authenticated:
        # If the user is authenticated, render the 'user_track.html.' template
        return render(request, 'user_track.html', {'userdata':userdata, 'visit_count': visit_count, 'today_total': today_total, 'monthly_total': monthly_total, 'yearly_total': yearly_total})
    else:
        # If the user is not authenticated, redirect to the home page
        return redirect('home')

def send_location(request, token): 

    # Get the user agent of the browser
    user_agent = request.META['HTTP_USER_AGENT']

    # Check if the provided token exists in the database
    if not TokenSummary.objects.filter(token=token).exists():
        return HttpResponse("Invalid token")

    # Get the user's submitted chat ID from the database
    token_summary = TokenSummary.objects.get(token=token)
    # chat id is used to sent message to login user
    chat_id = token_summary.chat_id 

    # Get the user associated with the token .this author is used to get the user's track record
    author = token_summary.author

    # Create a new Visit object using the create_visit function
    create_visit(author)

    # Get the user's visit count, today's total, monthly total, and yearly total
    visit_count = VisitCount.objects.get(author=author).visit_count
    today_total = VisitCount.objects.get(author=author).today_total
    monthly_total = VisitCount.objects.get(author=author).monthly_total
    yearly_total = VisitCount.objects.get(author=author).yearly_total
    
    # Get the user's IP address
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
    if ip is not None:
        # If the user is accessing the website through a proxy, get the first IP address in the list
        ip = ip.split(",")[0]

    # Use the 'ip-api.com' API to get the user's location
    # Note: The fields parameter specifies which fields to include in the response
    ip_url = f"http://ip-api.com/json/{ip}?fields=continent,country,region,regionName,city,district,zip,lat,lon,timezone,isp,org,as,asname,mobile,proxy,hosting,query"
    ip_response = requests.get(ip_url)   

    # Parse the response and extract the user's location
    ip_data = json.loads(ip_response.text)

    if "lat" in ip_data:
        lat = ip_data["lat"]
    if "lon" in ip_data:
        lon = ip_data["lon"]
    if "continent" in ip_data:
        continent = ip_data["continent"]
    if "country" in ip_data:
        country = ip_data["country"]
    if "region" in ip_data:
        region = ip_data["region"]
    if "regionName" in ip_data:
        region_name = ip_data["regionName"]
    if "city" in ip_data:
        city = ip_data["city"]
    if "district" in ip_data:
        district = ip_data["district"]
    if "zip" in ip_data:
        zip_code = ip_data["zip"]
    if "timezone" in ip_data:
        timezone = ip_data["timezone"]
    if "isp" in ip_data:
        isp = ip_data["isp"]
    if "org" in ip_data:
        org = ip_data["org"]
    if "as" in ip_data:
        as_number = ip_data["as"]
    if "asname" in ip_data:
        as_name = ip_data["asname"]
    if "mobile" in ip_data:
        mobile = ip_data["mobile"]
    if "proxy" in ip_data:
        proxy = ip_data["proxy"]
    if "hosting" in ip_data:
        hosting = ip_data["hosting"]
    if "query" in ip_data:
        ip_address = ip_data["query"]

    # Construct the message to be sent to the recipient
    message = ""
    if "query" in ip_data:
        message += "IP Address: " + ip_data["query"] + "\n"
    if "lat" in ip_data:
        message += "Latitude: " + str(ip_data["lat"]) + "\n"
    if "lon" in ip_data:
        message += "Longitude: " + str(ip_data["lon"]) + "\n"
    if "continent" in ip_data:
        message += "Continent: " + ip_data["continent"] + "\n"
    if "country" in ip_data:
        message += "Country: " + ip_data["country"] + "\n"
    if "region" in ip_data:
        message += "Region: " + ip_data["region"] + "\n"
    if "regionName" in ip_data:
        message += "Region Name: " + ip_data["regionName"] + "\n"
    if "city" in ip_data:
        message += "City: " + ip_data["city"] + "\n"
    if "district" in ip_data:
        message += "District: " + ip_data["district"] + "\n"
    if "zip" in ip_data:
        message += "Zip Code: " + ip_data["zip"] + "\n"
    if "timezone" in ip_data:
        message += "Time Zone: " + ip_data["timezone"] + "\n"
    if "isp" in ip_data:
        message += "ISP: " + ip_data["isp"] + "\n"
    if "org" in ip_data:
        message += "Organization: " + ip_data["org"] + "\n"
    if "as" in ip_data:
        message += "AS Number: " + ip_data["as"] + "\n"
    if "asname" in ip_data:
        message += "AS Name: " + ip_data["asname"] + "\n"
    if "mobile" in ip_data:
        message += "Mobile: {}\n".format(mobile)
    if "proxy" in ip_data:
        message += "Proxy:  {}\n".format(proxy)
    if "hosting" in ip_data:
        message += "Hosting: {}\n".format(hosting)

    # Include the Google Maps URL in the message
    if "lat" in ip_data and "lon" in ip_data:
        lat = ip_data["lat"]
        lon = ip_data["lon"]
        message += "Google Maps URL: " + f"https://www.google.com/maps/@{lat},{lon}" + "\n"

    # Get the current time
    current_time = datetime.now()
    message += "User Agent: " + user_agent + "\n"
    message += "Time: " + current_time.strftime("%I:%M %p") + "\n"
    message += "Date: " + current_time.strftime("%d/%m/%Y") + "\n"

    # Send the message to the  user's visit count, today's total, monthly total, and yearly total
    message += "Visits Today: " + str(today_total) + "\n"
    message += "Visits This Month: " + str(monthly_total) + "\n"
    message += "Visits This Year: " + str(yearly_total) + "\n"
    message += "Total Visits: " + str(visit_count) + "\n"


    # Use the get method to retrieve the values from the ip_data dictionary, and specify a default value if the key is not present 
    ip_address = ip_data.get("query", "")
    latitude = ip_data.get("lat", 0)
    longitude = ip_data.get("lon", 0)
    continent = ip_data.get("continent", "")
    country = ip_data.get("country", "")
    region = ip_data.get("region", "")
    region_name = ip_data.get("regionName", "")
    city = ip_data.get("city", "")
    district = ip_data.get("district", "")
    zip_code = ip_data.get("zip", "")
    timezone = ip_data.get("timezone", "")
    isp = ip_data.get("isp", "")
    org = ip_data.get("org", "")
    as_number = ip_data.get("as", "")
    as_name = ip_data.get("asname", "")
    mobile = ip_data.get("mobile", "")
    proxy = ip_data.get("proxy", "")
    hosting = ip_data.get("hosting", "")
    if "lat" in ip_data and "lon" in ip_data:
        lat = ip_data["lat"]
        lon = ip_data["lon"]
        map_link = f"https://www.google.com/maps/@{lat},{lon}"
    else:
        map_link = ""
        user_agent = request.headers.get("User-Agent")

    user_location = UserLocation(
        author=author,
        latitude=latitude,
        longitude=longitude,
        continent=continent,
        country=country,
        region=region,
        region_name=region_name,
        city=city,
        district=district,
        zip_code=zip_code,
        timezone=timezone,
        isp=isp,
        org=org,
        as_number=as_number,
        as_name=as_name,
        mobile=mobile,
        proxy=proxy,
        hosting=hosting,
        ip_address=ip_address,
        map_link=map_link,
        user_agent=user_agent,    
    )
    # Save the UserLocation object to the database
    user_location.save(request)

    # Use the 'sendMessage' method of the Telegram Bot API
    # to send the location information to the recipient
    send_message_url = f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendMessage"
    send_message_data = {"chat_id": chat_id, "text": message}
    send_message_response = requests.post(send_message_url, data=send_message_data)

    # Return a message to the user indicating that their location has been successfully sent
    return HttpResponse("202 Accepted")




@login_required
def token_summary(request):
    
    # Retrieve the authenticated user's 'TokenSummary' object
    token_summary = TokenSummary.objects.filter(author=request.user)

    # Query the TokenSummary model to get all the tokens that have been generated by the user
    tokens = TokenSummary.objects.filter(author=request.user)
    os.environ['SERVER_ADDRESS']

    # Check if the request method is POST
    if request.method == "POST":
        # Check if the user has already submitted a chat ID
        if TokenSummary.objects.filter(author=request.user).exists():
            # If the user has already submitted a chat ID, update it
            token_summary = TokenSummary.objects.get(author=request.user)
            token_summary.chat_id = request.POST["chat_id"]
            token_summary.save()
        else:
            # If the user has not submitted a chat ID, create a new record
            TokenSummary.objects.create(
                author=request.user, chat_id=request.POST["chat_id"]
            )

        # Redirect the user to the home page
        return redirect("token_summary")

    # Check if the user has submitted a chat ID
    if TokenSummary.objects.filter(author=request.user).exists():
        # If the user has submitted a chat ID, show the current chat ID
        token_summary = TokenSummary.objects.get(author=request.user)        

    
    # Add the SERVER_ADDRESS environment variable to the context dictionary
    context = {
        "chat_id": token_summary.chat_id,
        'token_summary': token_summary,
        'tokens': tokens,
        'SERVER_ADDRESS': os.environ['SERVER_ADDRESS'],
    }
    # Render the token_summary.html template and pass the token_summary and tokens objects as context variables
    return render(request, 'token_summary.html', context)


def create_visit(author):
    
    try:
        # Get the track record for the authenticated user
        visit = VisitCount.objects.get(author=author)
    except VisitCount.DoesNotExist:
        # If the object does not exist, create a new one
        visit = VisitCount.objects.create(author=author)

    # Get the current date and time
    current_date = datetime.now().date()
        
    # Increment the total visit count
    visit.visit_count += 1

    # Check if the day has changed since the last visit
    if visit.last_visit_date.day != current_date.day:
        # If the day has changed, reset the daily visit count
        visit.today_total = 0
    # Increment the daily visit count
    visit.today_total += 1

    # Check if the month has changed since the last visit
    if visit.last_visit_date.month != current_date.month:
        # If the month has changed, reset the monthly visit count
        visit.monthly_total = 0
    # Increment the monthly visit count
    visit.monthly_total += 1

    # Check if the year has changed since the last visit
    if visit.last_visit_date.year != current_date.year:
        # If the year has changed, reset the yearly visit count
        visit.yearly_total = 0
    # Increment the yearly visit count
    visit.yearly_total += 1

    # Update the last visit date
    visit.last_visit_date = current_date

    # Save the updated visit count to the database
    visit.save()

############## User track and send data start  ##############

##################### Data export start #####################

# export data as csv format
def export_csv(request):
    # get all user locations
    user_locations = UserLocation.objects.all()

    # create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_locations.csv"'

    # create the CSV writer
    writer = csv.writer(response)

    # write the header row
    writer.writerow(['Date', 'Time','Latitude', 'Longitude', 'Continent', 'Country', 'Region', 'Region Name', 'City', 'District', 'Zip Code', 'Timezone', 'ISP', 'Org', 'AS Number', 'AS Name', 'Mobile', 'Proxy', 'Hosting', 'IP Address', 'Map Link',  'User Agent'])

    # write the data rows
    for user_location in user_locations:
        writer.writerow([ user_location.latitude, user_location.longitude, user_location.continent, user_location.country, user_location.region, user_location.region_name, user_location.city, user_location.district, user_location.zip_code, user_location.timezone, user_location.isp, user_location.org, user_location.as_number, user_location.as_name, user_location.mobile, user_location.proxy, user_location.hosting, user_location.ip_address, user_location.map_link, user_location.date, user_location.time, user_location.user_agent])

    # return the response
    return response

# export data as json format
def export_json(request):
    user_locations = UserLocation.objects.all()
    data = [
        {
            'date': location.date.strftime("%d/%m/%Y"),
            'time': location.time.strftime("%H:%M:%S"),
            'latitude': location.latitude,
            'longitude': location.longitude,
            'continent': location.continent,
            'country': location.country,
            'region': location.region,
            'region_name': location.region_name,
            'city': location.city,
            'district': location.district,
            'zip_code': location.zip_code,
            'timezone': location.timezone,
            'isp': location.isp,
            'org': location.org,
            'as_number': location.as_number,
            'as_name': location.as_name,
            'mobile': location.mobile,
            'proxy': location.proxy,
            'hosting': location.hosting,
            'ip_address': location.ip_address,
            'map_link': location.map_link,
            'user_agent': location.user_agent,
        }
        for location in user_locations
    ]
    json_data = json.dumps(data)
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=user_locations.json'
    return response

# export data as excel format
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=user_locations.xls'

    tz = pytz.timezone('Asia/Kolkata')

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('UserLocations')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Date', 'Time','Latitude', 'Longitude', 'Continent', 'Country', 'Region', 'Region Name', 'City', 'District', 'Zip Code', 'Timezone', 'ISP', 'Org', 'AS Number', 'AS Name', 'Mobile', 'Proxy', 'Hosting', 'IP Address', 'Map Link',  'User Agent']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = UserLocation.objects.all().values_list('date', 'time', 'latitude', 'longitude', 'continent', 'country', 'region', 'region_name', 'city', 'district', 'zip_code', 'timezone', 'isp', 'org', 'as_number', 'as_name', 'mobile', 'proxy', 'hosting', 'ip_address', 'map_link', 'user_agent')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num == 20:
                # Set the time zone of the 'date' field
                ws.write(row_num, col_num, row[col_num].astimezone(tz).strftime("%d/%m/%Y"), font_style)
            elif col_num == 21:
                # Convert the 'time' field to a datetime object
                date = row[20]
                time = row[21]
                dt = datetime.combine(date, time, tz)
                ws.write(row_num, col_num, dt.strftime("%H:%M:%S"), font_style)
            else:
                ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

##################### Data export end #####################

#################### contact form #########################

def contact(request):
    return render(request,'contacts.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get the name and email fields from the form
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Create a new ContactFormData instance and save it to the database
            form_data = ContactFormData(name=name, email=email, message=message)
            form_data.save()

            # Get the current date and time
            now = datetime.now()

            # Format the date and time as a string
            time = now.strftime("%H:%M:%S")
            date = now.strftime("%m/%d/%Y")
            # Concatenate the name, email, message, and date/time into a single string to send to Telegram
            text = f'Hello, Administrator!\nName: {name}\nEmail: {email}\nMessage: {message}\nDate: {date}\nTime: {time}'

            # Send the message to the Telegram chat using the bot API
            chat_id = os.environ['CHAT_ID']
            bot_token = os.environ['BOT_TOKEN']
            requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', data={'chat_id': chat_id, 'text': text})

            # Redirect the user to the contact page
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contacts.html', {'form': form})

#################### contact form end ####################

