from discord.ext import commands,tasks
import discord
import random
import os
import asyncio
import requests
import urllib.parse # Add urllib.parse
import datetime
import io

# Environment variables kullan (Railway/Heroku için)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
intents.dm_messages = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None) # Disable default help command

Country = [
    ('US', 'United States'),
    ('AF', 'Afghanistan'),
    ('AL', 'Albania'),
    ('DZ', 'Algeria'),
    ('AS', 'American Samoa'),
    ('AD', 'Andorra'),
    ('AO', 'Angola'),
    ('AI', 'Anguilla'),
    ('AQ', 'Antarctica'),
    ('AG', 'Antigua And Barbuda'),
    ('AR', 'Argentina'),
    ('AM', 'Armenia'),
    ('AW', 'Aruba'),
    ('AU', 'Australia'),
    ('AT', 'Austria'),
    ('AZ', 'Azerbaijan'),
    ('BS', 'Bahamas'),
    ('BH', 'Bahrain'),
    ('BD', 'Bangladesh'),
    ('BB', 'Barbados'),
    ('BY', 'Belarus'),
    ('BE', 'Belgium'),
    ('BZ', 'Belize'),
    ('BJ', 'Benin'),
    ('BM', 'Bermuda'),
    ('BT', 'Bhutan'),
    ('BO', 'Bolivia'),
    ('BA', 'Bosnia And Herzegowina'),
    ('BW', 'Botswana'),
    ('BV', 'Bouvet Island'),
    ('BR', 'Brazil'),
    ('BN', 'Brunei Darussalam'),
    ('BG', 'Bulgaria'),
    ('BF', 'Burkina Faso'),
    ('BI', 'Burundi'),
    ('KH', 'Cambodia'),
    ('CM', 'Cameroon'),
    ('CA', 'Canada'),
    ('CV', 'Cape Verde'),
    ('KY', 'Cayman Islands'),
    ('CF', 'Central African Rep'),
    ('TD', 'Chad'),
    ('CL', 'Chile'),
    ('CN', 'China'),
    ('CX', 'Christmas Island'),
    ('CC', 'Cocos Islands'),
    ('CO', 'Colombia'),
    ('KM', 'Comoros'),
    ('CG', 'Congo'),
    ('CK', 'Cook Islands'),
    ('CR', 'Costa Rica'),
    ('CI', 'Cote D`ivoire'),
    ('HR', 'Croatia'),
    ('CU', 'Cuba'),
    ('CY', 'Cyprus'),
    ('CZ', 'Czech Republic'),
    ('DK', 'Denmark'),
    ('DJ', 'Djibouti'),
    ('DM', 'Dominica'),
    ('DO', 'Dominican Republic'),
    ('TP', 'East Timor'),
    ('EC', 'Ecuador'),
    ('EG', 'Egypt'),
    ('SV', 'El Salvador'),
    ('GQ', 'Equatorial Guinea'),
    ('ER', 'Eritrea'),
    ('EE', 'Estonia'),
    ('ET', 'Ethiopia'),
    ('FK', 'Falkland Islands (Malvinas)'),
    ('FO', 'Faroe Islands'),
    ('FJ', 'Fiji'),
    ('FI', 'Finland'),
    ('FR', 'France'),
    ('GF', 'French Guiana'),
    ('PF', 'French Polynesia'),
    ('TF', 'French S. Territories'),
    ('GA', 'Gabon'),
    ('GM', 'Gambia'),
    ('GE', 'Georgia'),
    ('DE', 'Germany'),
    ('GH', 'Ghana'),
    ('GI', 'Gibraltar'),
    ('GR', 'Greece'),
    ('GL', 'Greenland'),
    ('GD', 'Grenada'),
    ('GP', 'Guadeloupe'),
    ('GU', 'Guam'),
    ('GT', 'Guatemala'),
    ('GN', 'Guinea'),
    ('GW', 'Guinea-bissau'),
    ('GY', 'Guyana'),
    ('HT', 'Haiti'),
    ('HN', 'Honduras'),
    ('HK', 'Hong Kong'),
    ('HU', 'Hungary'),
    ('IS', 'Iceland'),
    ('IN', 'India'),
    ('ID', 'Indonesia'),
    ('IR', 'Iran'),
    ('IQ', 'Iraq'),
    ('IE', 'Ireland'),
    ('IL', 'Israel'),
    ('IT', 'Italy'),
    ('JM', 'Jamaica'),
    ('JP', 'Japan'),
    ('JO', 'Jordan'),
    ('KZ', 'Kazakhstan'),
    ('KE', 'Kenya'),
    ('KI', 'Kiribati'),
    ('KP', 'Korea (North)'),
    ('KR', 'Korea (South)'),
    ('KW', 'Kuwait'),
    ('KG', 'Kyrgyzstan'),
    ('LA', 'Laos'),
    ('LV', 'Latvia'),
    ('LB', 'Lebanon'),
    ('LS', 'Lesotho'),
    ('LR', 'Liberia'),
    ('LY', 'Libya'),
    ('LI', 'Liechtenstein'),
    ('LT', 'Lithuania'),
    ('LU', 'Luxembourg'),
    ('MO', 'Macau'),
    ('MK', 'Macedonia'),
    ('MG', 'Madagascar'),
    ('MW', 'Malawi'),
    ('MY', 'Malaysia'),
    ('MV', 'Maldives'),
    ('ML', 'Mali'),
    ('MT', 'Malta'),
    ('MH', 'Marshall Islands'),
    ('MQ', 'Martinique'),
    ('MR', 'Mauritania'),
    ('MU', 'Mauritius'),
    ('YT', 'Mayotte'),
    ('MX', 'Mexico'),
    ('FM', 'Micronesia'),
    ('MD', 'Moldova'),
    ('MC', 'Monaco'),
    ('MN', 'Mongolia'),
    ('MS', 'Montserrat'),
    ('ME', 'Montenegro'),
    ('MA', 'Morocco'),
    ('MZ', 'Mozambique'),
    ('MM', 'Myanmar'),
    ('NA', 'Namibia'),
    ('NR', 'Nauru'),
    ('NP', 'Nepal'),
    ('NL', 'Netherlands'),
    ('AN', 'Netherlands Antilles'),
    ('NC', 'New Caledonia'),
    ('NZ', 'New Zealand'),
    ('NI', 'Nicaragua'),
    ('NE', 'Niger'),
    ('NG', 'Nigeria'),
    ('NU', 'Niue'),
    ('NF', 'Norfolk Island'),
    ('MP', 'Northern Mariana Islands'),
    ('NO', 'Norway'),
    ('OM', 'Oman'),
    ('PK', 'Pakistan'),
    ('PW', 'Palau'),
    ('PA', 'Panama'),
    ('PG', 'Papua New Guinea'),
    ('PY', 'Paraguay'),
    ('PE', 'Peru'),
    ('PH', 'Philippines'),
    ('PN', 'Pitcairn'),
    ('PL', 'Poland'),
    ('PT', 'Portugal'),
    ('PR', 'Puerto Rico'),
    ('QA', 'Qatar'),
    ('RE', 'Reunion'),
    ('RO', 'Romania'),
    ('RU', 'Russian Federation'),
    ('RW', 'Rwanda'),
    ('KN', 'Saint Kitts And Nevis'),
    ('LC', 'Saint Lucia'),
    ('VC', 'St Vincent/Grenadines'),
    ('WS', 'Samoa'),
    ('SM', 'San Marino'),
    ('ST', 'Sao Tome'),
    ('SA', 'Saudi Arabia'),
    ('SN', 'Senegal'),
    ('SC', 'Seychelles'),
    ('SL', 'Sierra Leone'),
    ('SG', 'Singapore'),
    ('SK', 'Slovakia'),
    ('SI', 'Slovenia'),
    ('SB', 'Solomon Islands'),
    ('SO', 'Somalia'),
    ('ZA', 'South Africa'),
    ('ES', 'Spain'),
    ('LK', 'Sri Lanka'),
    ('SH', 'St. Helena'),
    ('PM', 'St.Pierre'),
    ('SD', 'Sudan'),
    ('SR', 'Suriname'),
    ('SZ', 'Swaziland'),
    ('SE', 'Sweden'),
    ('CH', 'Switzerland'),
    ('SY', 'Syrian Arab Republic'),
    ('TW', 'Taiwan'),
    ('TJ', 'Tajikistan'),
    ('TZ', 'Tanzania'),
    ('TH', 'Thailand'),
    ('TG', 'Togo'),
    ('TK', 'Tokelau'),
    ('TO', 'Tonga'),
    ('TT', 'Trinidad And Tobago'),
    ('TN', 'Tunisia'),
    ('TR', 'Turkey'),
    ('TM', 'Turkmenistan'),
    ('TV', 'Tuvalu'),
    ('UG', 'Uganda'),
    ('UA', 'Ukraine'),
    ('AE', 'United Arab Emirates'),
    ('UK', 'United Kingdom'),
    ('UY', 'Uruguay'),
    ('UZ', 'Uzbekistan'),
    ('VU', 'Vanuatu'),
    ('VA', 'Vatican City State'),
    ('VE', 'Venezuela'),
    ('VN', 'Viet Nam'),
    ('VG', 'Virgin Islands (British)'),
    ('VI', 'Virgin Islands (U.S.)'),
    ('EH', 'Western Sahara'),
    ('YE', 'Yemen'),
    ('ZR', 'Zaire'),
    ('ZM', 'Zambia'),
    ('ZW', 'Zimbabwe'),
    ('RS', 'Serbia'),

]

def to_upper(argument):
    return argument.upper()
def to_lower(argument):
    return argument.lower()


@bot.event
async def on_ready():
    print("Hello, Imposter BOT is ready!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("naber")
@bot.event
async def on_message(message: discord.Message):
    # Bot kendi mesajlarını işlemesin
    if message.author.bot:
        return
    
    server = bot.get_guild(1071184228382937209)
    vrole = discord.utils.find(lambda m: m.id == 1071184541500321842, server.roles)
    richRole = discord.utils.find(lambda m: m.id == 1086688797229580318, server.roles)
    kaiserRole = discord.utils.find(lambda m: m.id == 1071184295646998620, server.roles)

    # Belirli bir kelimeyi kontrol etme
    if "dollar" in message.content.lower(): # Buraya aranan kelimeyi yazın (küçük harfle)
        await message.channel.send("ooo thatsabigbrablem") # Buraya cevabı yazın

    # Yasaklı kelime kontrolü ve silme
    yasakli_kelime = "epstein" # Silinmesini istediğiniz kelimeyi buraya yazın
    if yasakli_kelime in message.content.lower() and message.author.id != bot.user.id:
        try:
            await message.delete()
            await message.channel.send(f"not a good goy", delete_after=3)
            return # Mesaj silindiyse fonksiyondan çık
        except discord.Forbidden:
            print("Mesajı silmek için yetkim yok.")

    if '!' in message.content and not message.content.startswith('!'): #bot id
        await message.delete()

    # Komutları en sonda işle
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """
    Handles voice state updates to make the bot leave if it's alone in a channel.
    """
    # Ignore events triggered by the bot itself to avoid loops or unwanted disconnections
    if member.id == bot.user.id:
        return

    voice_client = member.guild.voice_client

    # Check if the bot is connected to a voice channel in this guild
    if voice_client and voice_client.is_connected():
        # Check if the event is about a user leaving the channel the bot is in
        if before.channel == voice_client.channel and after.channel != voice_client.channel:
            # Short delay to allow member list to update, though often not strictly necessary
            # await asyncio.sleep(0.5) 
            
            # Check current members in the bot's channel
            current_channel_members = voice_client.channel.members
            human_users_in_channel = [m for m in current_channel_members if not m.bot]

            if not human_users_in_channel:
                print(f"Bot is now alone in '{voice_client.channel.name}' (Guild: {member.guild.name}). Disconnecting.")
                await voice_client.disconnect()

@bot.command()
async def length(ctx, *args):
    arguments = ', '.join(args)
    await ctx.send(f"{len(args)} kelime: {arguments}")

@bot.command()
async def up(ctx, *, content: to_upper):
    await ctx.send(content)

@bot.command()
async def down(ctx, *, content: to_lower):
    await ctx.send(content)

@bot.command()
async def nickname(ctx, *, user: discord.User):
    await ctx.send(user.id)

@bot.command()
async def dm(ctx, user: discord.User, *, message): 
    await user.send(message)

@bot.command()
async def joke(ctx):
    """Fetches a random joke (setup and punchline)."""
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        joke_data = response.json()
        setup = joke_data.get('setup')
        punchline = joke_data.get('punchline')
        
        if setup and punchline:
            await ctx.send(f"{setup} ||{punchline}||") # Punchline in spoiler
        else:
            await ctx.send("Sorry, I couldn't get a complete joke from the API.")
            print(f"Joke API response missing setup or punchline: {joke_data}")
            
    except requests.exceptions.Timeout:
        await ctx.send("Sorry, the joke service timed out. Please try again later.")
    except requests.exceptions.HTTPError as e:
        await ctx.send(f"Sorry, the joke service returned an error: {e.response.status_code} - {e.response.reason}.")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Sorry, there was an error communicating with the joke service: {type(e).__name__}.")
    except Exception as e:
        await ctx.send("An unexpected error occurred while trying to fetch a joke.")
        print(f"Unexpected error in !joke command: {type(e).__name__} - {e}")

@bot.command()
async def weather(ctx, *, city_name: str):
    """Fetches current weather for a given city."""
    try:
        encoded_city_name = urllib.parse.quote(city_name)
        
        processing_message = await ctx.send(f"🌤️ Fetching weather for \"{city_name}\"...")

        # Step 1: Geocode the city name to get latitude, longitude, and timezone
        geo_api_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city_name}&count=1&language=en&format=json"
        
        geo_response = requests.get(geo_api_url, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results") or len(geo_data["results"]) == 0:
            await processing_message.edit(content=f"Sorry, I couldn't find location data for \"{city_name}\". Please check the city name and try again.")
            return

        location_data = geo_data["results"][0]
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")
        timezone = location_data.get("timezone", "auto") # Default to 'auto' if not found, Open-Meteo can handle it
        display_city_name = location_data.get("name", city_name)
        country = location_data.get("country", "")
        admin1 = location_data.get("admin1", "")

        if latitude is None or longitude is None:
            await processing_message.edit(content=f"Sorry, I couldn't get precise coordinates for \"{city_name}\".")
            return

        # Step 2: Fetch weather using the obtained latitude, longitude, and timezone
        weather_api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&timezone={timezone}"
        
        weather_response = requests.get(weather_api_url, timeout=10)
        weather_response.raise_for_status()  # Raise an HTTPError for bad responses

        weather_data = weather_response.json()

        if 'current_weather' in weather_data:
            current_weather = weather_data['current_weather']
            temperature = current_weather.get('temperature', 'N/A')
            windspeed = current_weather.get('windspeed', 'N/A')
            winddirection = current_weather.get('winddirection', 'N/A')
            time_str = current_weather.get('time', 'N/A')
            
            # Format the time for better readability if possible
            try:
                if time_str != 'N/A':
                    dt_object = datetime.datetime.fromisoformat(time_str)
                    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M')
                else:
                    formatted_time = 'N/A'
            except ValueError:
                formatted_time = time_str # Keep original if parsing fails

            location_display = f"{display_city_name}"
            if admin1:
                location_display += f", {admin1}"
            if country:
                location_display += f", {country}"

            await processing_message.edit(content=f"**Weather in {location_display}:**\nTemperature: {temperature}°C\nWindspeed: {windspeed} km/h\nWind Direction: {winddirection}°\nTime: {formatted_time} ({timezone})")
        else:
            await processing_message.edit(content=f"Sorry, I couldn't find the weather for \"{display_city_name}\". The API returned no current weather data.")

    except requests.exceptions.Timeout:
        await processing_message.edit(content="Sorry, the weather or location service timed out. Please try again later.")
    except requests.exceptions.HTTPError as e:
        await processing_message.edit(content=f"Sorry, a service returned an error: {e.response.status_code}. Please try again.")
    except requests.exceptions.RequestException as e:
        await processing_message.edit(content=f"Sorry, there was an error communicating with one of the services: {type(e).__name__}.")
    except Exception as e:
        await processing_message.edit(content="An unexpected error occurred while trying to fetch weather data.")
        print(f"Unexpected error in !weather command: {type(e).__name__} - {e}")

@bot.command()
async def paint(ctx, *, prompt: str):
    """Generates an image from a text prompt using Pollinations.ai"""
    processing_message = await ctx.send(f"🎨 Generating an image for: \"{prompt}\". Please wait, this might take a moment...")
    
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        # Example: api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}%20photorealistic%20epic"
        api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        
        loop = asyncio.get_event_loop()
        # Use a timeout for the request, Pollinations can be slow
        response = await loop.run_in_executor(None, lambda: requests.get(api_url, timeout=90)) 

        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        content_type = response.headers.get('Content-Type', '').lower()
        if 'image' in content_type:
            image_bytes = response.content
            # Create a filename from the prompt, sanitizing it
            safe_filename_prompt = "".join(c if c.isalnum() else "_" for c in prompt)[:50]
            filename = f"{safe_filename_prompt}.jpg"

            with io.BytesIO(image_bytes) as image_file_buffer:
                await ctx.send(file=discord.File(image_file_buffer, filename=filename))
            await processing_message.delete() # Delete "Generating..." message
        else:
            await processing_message.edit(content=f"Sorry, I received an unexpected response from the image service. (Content-Type: {content_type})")
            print(f"Pollinations API did not return an image. Content-Type: {content_type}, Status: {response.status_code}, Response: {response.text[:200]}")

    except requests.exceptions.Timeout:
        await processing_message.edit(content="Sorry, the image generation timed out. Please try again later or with a simpler prompt.")
    except requests.exceptions.HTTPError as e:
        error_message = f"Sorry, the image service returned an error: {e.response.status_code} - {e.response.reason}."
        if e.response.status_code == 403: # Forbidden, often due to content filter
             error_message += " This might be due to the prompt triggering a content filter on the image service."
        await processing_message.edit(content=error_message)
        print(f"HTTPError with Pollinations API: {e}")
    except requests.exceptions.RequestException as e: # Catch other request-related errors
        await processing_message.edit(content=f"Sorry, there was an error communicating with the image generation service: {type(e).__name__}.")
        print(f"RequestException with Pollinations API: {e}")
    except Exception as e:
        await processing_message.edit(content=f"An unexpected error occurred while trying to generate the image.")
        print(f"Unexpected error in !paint command: {type(e).__name__} - {e}")

@bot.command()
async def fact(ctx):
    """Get a random fun fact"""
    try:
        api_url = 'https://uselessfacts.jsph.pl/random.json'
        response = requests.get(api_url)
        
        if response.status_code == 200:
            fact_data = response.json()
            fact = fact_data.get('text', 'No fact available')
            await ctx.send(f"**Fun Fact:** {fact}")
        else:
            await ctx.send(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def location(ctx, *, city_name: str):
    """Fetches latitude and longitude for a given city."""
    try:
        encoded_city_name = urllib.parse.quote(city_name)
        api_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city_name}&count=1&language=en&format=json"
        
        processing_message = await ctx.send(f"🔍 Looking up coordinates for \"{city_name}\"...")

        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        data = response.json()

        if data.get("results") and len(data["results"]) > 0:
            location_data = data["results"][0]
            latitude = location_data.get("latitude")
            longitude = location_data.get("longitude")
            name = location_data.get("name", city_name)
            country = location_data.get("country", "N/A")
            admin1 = location_data.get("admin1", "") # State or region

            await processing_message.edit(content=f"**Location:** {name}, {admin1 + ', ' if admin1 else ''}{country} **Latitude:** {latitude} **Longitude:** {longitude}")
        else:
            await processing_message.edit(content=f"Sorry, I couldn't find coordinates for \"{city_name}\". Please check the city name and try again.")

    except requests.exceptions.Timeout:
        await processing_message.edit(content="Sorry, the location service timed out. Please try again later.")
    except requests.exceptions.HTTPError as e:
        await processing_message.edit(content=f"Sorry, the location service returned an error: {e.response.status_code}. Please try again.")
    except requests.exceptions.RequestException as e:
        await processing_message.edit(content=f"Sorry, there was an error communicating with the location service: {type(e).__name__}.")
    except Exception as e:
        await processing_message.edit(content="An unexpected error occurred while trying to fetch location data.")
        print(f"Unexpected error in !location command: {type(e).__name__} - {e}")

@bot.command()
async def satellite(ctx, *, city_name: str):
    """Fetches satellite pass data for a given city."""
    try:
        encoded_city_name = urllib.parse.quote(city_name)
        geo_api_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city_name}&count=1&language=en&format=json"
        
        processing_message = await ctx.send(f"🛰️ Looking up coordinates and satellite passes for \"{city_name}\"...")

        # 1. Get Latitude and Longitude
        geo_response = requests.get(geo_api_url, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data.get("results") or len(geo_data["results"]) == 0:
            await processing_message.edit(content=f"Sorry, I couldn't find coordinates for \"city_name\". Please check the city name.")
            return

        location_data = geo_data["results"][0]
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")
        found_city_name = location_data.get("name", city_name)
        country = location_data.get("country", "")

        if latitude is None or longitude is None:
            await processing_message.edit(content=f"Sorry, I found \"{found_city_name}\" but couldn't get its exact coordinates.")
            return

        await processing_message.edit(content=f"Coordinates found for {found_city_name}, {country} (Lat: {latitude:.4f}, Lon: {longitude:.4f}). Fetching satellite passes...")

        # 2. Get Satellite Data
        satellite_api_url = f"https://sat.terrestre.ar/passes/25544?lat={latitude}&lon={longitude}&limit=1"
        sat_response = requests.get(satellite_api_url, timeout=15) # Increased timeout for this API
        sat_response.raise_for_status()
        passes_data = sat_response.json()

        if not passes_data or not isinstance(passes_data, list) or len(passes_data) == 0:
            await processing_message.edit(content=f"No satellite pass data found for {found_city_name} at this time.")
            return

        # Assuming we want to display the first pass from the limit=1 API call
        pass_info = passes_data[0]
        
        # Helper to convert UTC timestamp to a more readable format
        def format_pass_time(timestamp_utc):
            if timestamp_utc is None:
                return "N/A"
            dt_object = datetime.datetime.fromtimestamp(timestamp_utc, tz=datetime.timezone.utc)
            return dt_object.strftime('%Y-%m-%d %H:%M:%S %Z')

        # Access nested data for AOS, LOS, and Max Elevation
        rise_data = pass_info.get('rise', {})
        set_data = pass_info.get('set', {})
        culmination_data = pass_info.get('culmination', {})

        aos_utc_val = rise_data.get('utc_timestamp')
        los_utc_val = set_data.get('utc_timestamp')
        max_elevation_deg = culmination_data.get('alt', 'N/A') # 'alt' often used for altitude/elevation

        # Get sunlit and visibility info
        rise_sunlit = rise_data.get('is_sunlit', 'N/A')
        rise_visible = rise_data.get('visible', 'N/A')
        culmination_sunlit = culmination_data.get('is_sunlit', 'N/A')
        culmination_visible = culmination_data.get('visible', 'N/A')
        set_sunlit = set_data.get('is_sunlit', 'N/A')
        set_visible = set_data.get('visible', 'N/A')

        aos_time = format_pass_time(aos_utc_val)
        los_time = format_pass_time(los_utc_val)
        # max_elevation_deg is already fetched, ensure it's formatted if it's a number
        # duration_sec, orbit, and direction are assumed to be potentially top-level or handled correctly

        # Get specific directions for each phase
        rise_direction = rise_data.get('az_octant', 'N/A')
        culmination_direction = culmination_data.get('az_octant', 'N/A')
        set_direction = set_data.get('az_octant', 'N/A')

        embed = discord.Embed(
            title=f"🛰️ Satellite Pass Over {found_city_name}, {country}",
            description=f"Details for the next pass of satellite NOAA 19 (ID: 25544).",
            color=discord.Color.blue()
        )
        embed.add_field(name="Acquisition of Signal (AOS)", value=f"{aos_time}\nDirection: {rise_direction}\nSunlit: {rise_sunlit}, Visible: {rise_visible}", inline=False)
        embed.add_field(name="Loss of Signal (LOS)", value=f"{los_time}\nDirection: {set_direction}\nSunlit: {set_sunlit}, Visible: {set_visible}", inline=False)
        embed.add_field(name="Max Elevation", value=f"{max_elevation_deg}°\nDirection: {culmination_direction}\nSunlit: {culmination_sunlit}, Visible: {culmination_visible}", inline=True)
        embed.set_footer(text=f"Coordinates: Lat {latitude:.4f}, Lon {longitude:.4f}")

        await processing_message.delete() # Delete the "processing..." message
        await ctx.send(embed=embed)

    except requests.exceptions.Timeout as e:
        await processing_message.edit(content=f"Sorry, a service timed out while fetching satellite data for \"{city_name}\". Please try again. ({type(e).__name__})")
    except requests.exceptions.HTTPError as e:
        await processing_message.edit(content=f"Sorry, a service returned an error: {e.response.status_code}. (URL: {e.request.url})")
    except requests.exceptions.RequestException as e:
        await processing_message.edit(content=f"Sorry, there was an error communicating with one of the services: {type(e).__name__}.")
    except Exception as e:
        await processing_message.edit(content="An unexpected error occurred while trying to fetch satellite data.")
        print(f"Unexpected error in !satellite command for city '{city_name}': {type(e).__name__} - {e}")

# Müzik sistemi - FFmpeg/yt-dlp
import yt_dlp

YDL_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

song_queues = {}  # guild_id: [{'url': str, 'title': str}]

async def play_next(ctx):
    guild_id = ctx.guild.id
    if guild_id in song_queues and song_queues[guild_id]:
        song = song_queues[guild_id][0]
        
        voice_client = ctx.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            return
        
        def after_playing(error):
            if error:
                print(f"Player error: {error}")
            if guild_id in song_queues and song_queues[guild_id]:
                song_queues[guild_id].pop(0)
            asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        
        source = discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS)
        voice_client.play(source, after=after_playing)
        await ctx.send(f"🎵 Now playing: **{song['title']}**")
    else:
        if guild_id in song_queues:
            del song_queues[guild_id]

@bot.command()
async def join(ctx):
    """Bot ses kanalına katılır"""
    if not ctx.author.voice:
        await ctx.send("Önce bir ses kanalına bağlanmalısın!")
        return
    
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
    await ctx.send(f"🔊 **{channel.name}** kanalına katıldım!")

@bot.command()
async def leave(ctx):
    """Bot ses kanalından ayrılır"""
    if ctx.voice_client:
        guild_id = ctx.guild.id
        if guild_id in song_queues:
            del song_queues[guild_id]
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Ses kanalından ayrıldım!")
    else:
        await ctx.send("Zaten bir ses kanalında değilim.")

@bot.command()
async def play(ctx, *, query: str):
    """Şarkı çalar veya kuyruğa ekler"""
    if not ctx.author.voice:
        await ctx.send("Önce bir ses kanalına bağlanmalısın!")
        return
    
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)
    
    processing_msg = await ctx.send(f"🔍 Aranıyor: **{query}**...")
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            if not query.startswith('http'):
                query = f"ytsearch:{query}"
            info = ydl.extract_info(query, download=False)
            
            if 'entries' in info:
                info = info['entries'][0]
            
            url = info['url']
            title = info.get('title', 'Bilinmeyen şarkı')
            
            guild_id = ctx.guild.id
            if guild_id not in song_queues:
                song_queues[guild_id] = []
            
            song_queues[guild_id].append({'url': url, 'title': title})
            
            if not ctx.voice_client.is_playing():
                await processing_msg.delete()
                await play_next(ctx)
            else:
                await processing_msg.edit(content=f"📝 Kuyruğa eklendi: **{title}**")
    
    except Exception as e:
        await processing_msg.edit(content=f"❌ Hata: {str(e)}")
        print(f"Play error: {e}")

@bot.command()
async def skip(ctx):
    """Mevcut şarkıyı atlar"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Şarkı atlandı!")
    else:
        await ctx.send("Şu anda çalan bir şarkı yok.")

@bot.command()
async def stop(ctx):
    """Müziği durdurur ve kuyruğu temizler"""
    guild_id = ctx.guild.id
    if guild_id in song_queues:
        song_queues[guild_id] = []
    
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ Müzik durduruldu ve kuyruk temizlendi!")
    else:
        await ctx.send("Zaten bir şey çalmıyor.")

@bot.command()
async def queue(ctx):
    """Şarkı kuyruğunu gösterir"""
    guild_id = ctx.guild.id
    if guild_id not in song_queues or not song_queues[guild_id]:
        await ctx.send("📭 Kuyruk boş!")
        return
    
    queue_list = ""
    for i, song in enumerate(song_queues[guild_id]):
        if i == 0:
            queue_list += f"🎵 **Şu an çalıyor:** {song['title']}\n\n"
        else:
            queue_list += f"{i}. {song['title']}\n"
    
    await ctx.send(f"**📜 Şarkı Kuyruğu:**\n{queue_list}")

@bot.command()
async def pause(ctx):
    """Müziği duraklatır"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Müzik duraklatıldı!")
    else:
        await ctx.send("Şu anda çalan bir şarkı yok.")

@bot.command()
async def resume(ctx):
    """Duraklatılmış müziği devam ettirir"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Müzik devam ediyor!")
    else:
        await ctx.send("Duraklatılmış bir şarkı yok.")

async def main():
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())