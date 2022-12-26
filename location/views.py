import json
import os
from sqlite3 import IntegrityError
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
from datetime import date, datetime
from .forms import UserCreateForm
from .models import *





def contact(request):
    return render(request,'contacts.html')

def home(request):
    return render(request,'home.html')

def login_view(request):
    if request.method == 'GET':
        return render(request, 'registration/login.html',{'form':AuthenticationForm})
    user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
    if user is None:
        return render(request,'registration/login.html',{'form': AuthenticationForm(),'error': 'username and password do not match'})
    login(request,user)
    return redirect('home')

@login_required
def logoutaccount(request):
    logout(request)
    return redirect('home')

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

    # Check if the provided username already exists in the database
    if User.objects.filter(username=request.POST["username"]).exists():
        # If the username already exists, display an error message
        return render(
            request,
            "registration/register.html",
            {"form": UserCreateForm, "error": "Username already taken. Choose new username."},
        )

    try:
        # Create a new user using the provided username and password
        author = User.objects.create_user(
            request.POST["username"], 
            password=request.POST["password1"]

        )
        login(request, author)

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

        # Redirect the user to the home page
        return redirect("home")
    except IntegrityError:
        # If the username is already taken, display an error message
        return render(
            request,
            "registration/register.html",
            {"form": UserCreateForm, "error": "Username already taken. Choose new username."},
        )











@login_required
def user_track(request):
    # Get the visit count, today's total, monthly total, and yearly total for the authenticated user
    visit_count = VisitCount.objects.get(author=request.user).visit_count
    today_total = VisitCount.objects.get(author=request.user).today_total
    monthly_total = VisitCount.objects.get(author=request.user).monthly_total
    yearly_total = VisitCount.objects.get(author=request.user).yearly_total

    # data is display to deseding order
    userdata = UserLocation.objects.order_by('-date', '-time')
    

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
        message += "Mobile: " + ip_data["mobile"] + "\n"
    if "proxy" in ip_data:
        message += "Proxy: " + ip_data["proxy"] + "\n"
    if "hosting" in ip_data:
        message += "Hosting: " + ip_data["hosting"] + "\n"

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
    # Get the current date and time
    current_date = datetime.now().date()

    # Get the track record for the authenticated user, or create a new one if it doesn't exist
    visit, created = VisitCount.objects.get_or_create(
        author=author,
    )

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


#############################################################################################################

