import requests
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import WeatherSearch

def get_daily_min_max(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&lang=ua&units=metric"
    response = requests.get(url)
    data = response.json()
    today = datetime.utcnow().date()
    temps = [item['main']['temp'] for item in data.get('list', [])
             if datetime.utcfromtimestamp(item['dt']).date() == today]
    if temps:
        return min(temps), max(temps)
    return None, None

@login_required
def main_view(request):
    weather = None
    city_time = None
    weather_class = "weather-default"
    if request.method == "POST":
        city = request.POST.get("city")
        API_KEY = "e90fab7014064d2c88795d9fd95afa6f"
        url_now = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=ua&units=metric"
        response_now = requests.get(url_now)
        data_now = response_now.json()
        if data_now.get("cod") == 200:
            temp_min, temp_max = get_daily_min_max(city, API_KEY)
            current_temp = round(data_now["main"]["temp"])
            if temp_min is not None:
                temp_min = min(round(temp_min), current_temp)
            else:
                temp_min = current_temp
            if temp_max is not None:
                temp_max = max(round(temp_max), current_temp)
            else:
                temp_max = current_temp
            sunrise = datetime.fromtimestamp(data_now["sys"]["sunrise"] + data_now["timezone"])
            sunset = datetime.fromtimestamp(data_now["sys"]["sunset"] + data_now["timezone"])
            utc_now = datetime.utcnow()
            city_time = utc_now + timedelta(seconds=data_now["timezone"])
            wind_deg = data_now["wind"].get("deg", 0)
            main_weather = data_now["weather"][0]["main"].lower()
            if "rain" in main_weather:
                weather_class = "weather-rain"
            elif "cloud" in main_weather:
                weather_class = "weather-cloud"
            elif "clear" in main_weather:
                weather_class = "weather-clear"
            elif "snow" in main_weather:
                weather_class = "weather-snow"
            elif "thunderstorm" in main_weather:
                weather_class = "weather-thunder"
            else:
                weather_class = "weather-default"
            weather = {
                "city": city,
                "temperature": current_temp,
                "temp_min": temp_min,
                "temp_max": temp_max,
                "description": data_now["weather"][0]["description"].capitalize(),
                "icon": data_now["weather"][0]["icon"],
                "feels_like": round(data_now["main"]["feels_like"]),
                "humidity": data_now["main"]["humidity"],
                "pressure": data_now["main"]["pressure"],
                "wind": round(data_now["wind"]["speed"]),
                "wind_deg": wind_deg,
                "sunrise": sunrise.strftime('%H:%M'),
                "sunset": sunset.strftime('%H:%M'),
                "weather_main": main_weather,
            }
            WeatherSearch.objects.create(
                user=request.user,
                city=city,
                temperature=current_temp,
                description=weather["description"]
            )
        else:
            messages.error(request, "Місто не знайдено.")
    return render(request, "main.html", {
        "weather": weather,
        "city_time": city_time,
        "weather_class": weather_class
    })

@login_required
def history_view(request):
    history = WeatherSearch.objects.filter(user=request.user).order_by("-search_date")[:20]
    return render(request, "history.html", {"history": history})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("main")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("main")
        else:
            messages.error(request, "Невірний логін або пароль.")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def register_view(request):
    if request.user.is_authenticated:
        return redirect("main")
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Ви успішно зареєструвалися!")
            return redirect("main")
        else:
            messages.error(request, "Будь ласка, виправте помилки у формі.")
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})