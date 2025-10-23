import logging
from struct import pack
import re, os
import asyncio
import base64
import pymongo
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DB_URI, DB_NAME, LOG_CHANNEL, COLLECTION_NAME, BOT_TOKEN, API_ID, API_HASH
from database.toptrending import top
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO


SPELL_WORDS = ["Dilpreet Dhillon Feat. Gurlej Akhtar", "(", ")", "457", "Review", "spoilers", "Special", "BFH", "Bonus 5", "Part", "part", "Movies and Specials to Stream", "Season", "season", "HD", "hd", "Horror Movie", "IT and the Upside Down of Nostalgia", "?", "None", ":", "'", ",", "episode", "Episode", "Movie Review", "Ms. Marvel Trailer, X Horror Movie Review - Episode 93"]

#username remove

BLACKLIST_WORDS = (
    list(os.environ.get("BLACKLIST_WORDS").split(","))
    if os.environ.get("BLACKLIST_WORDS")
    else []
)

BLACKLIST_WORDS = ["[Telegram@alpacinodump], {_@NRDramaa_}, www.1TamilMV.dad, @SH_OTT, @New_Movies_1stOnTG", "www_TamilBlasters_bond", "[Telegram@alpacinodump]", "tg @Bollyarchives ", "@Netflix_Villa_Original", "@Netflix Villa Original", "{_@NRDramaa_}", "www_SkymoviesHD", "@FBM_HW", "[CF]", "[ᎡᴛᏴᴛ]", "@CK_HEVC", "@Tamil LinkzZ", "@SY MS", "SkymoviesHD", "www 1TamilMV zip", "a8ix live", "@Cinematic_world", "SkymoviesHD", "@MoViEsWeB HeVc", "Filmy4Cab com", "www 7MovieRulz mn", "www 1TamilMV vin", "www 1TamilMV win", "www 1TamilMV cafe", "@ADrama  Lovers", "www 1TamilMV help", "KC", "@CK Moviez", "E4E", "[BindasMovies]", "[Hezz Series]", "[Hezz Movies]", "[CC]", "www Tamilblasters rent", "[CH]", "www 4MovieRulz com", "www.TamiLRockers.com.avi", "www_1TamilMV_fun", "www_DVDWap_com", "www.TamilRockers.fi", "www TamilBlasters cam", "www Tamilblasters social", "[@The 4x Team]", "@mj link 4u", "[CD]", "@Andhra movies", "@BT MOVIES HD", "@Team_HDT", "Telegram@APDBackup", "Telegram@Alpacinodump", "www 1TamilMV fans", "@Ruraljat Studio", "7HitMovies bio", "[MZM]", "[@UCMOVIE]", "@CC_New", "[MF]", "@Mallu_Movies", "[MC]", "[@MociesVerse]", "@Mm_Linkz", "@BT_MOVIES_HD_@FILMSCLUB04", "www TamilVaathi online", "www 1TamilMV mx", "@BGM LinkzZ", "www 1TamilMV media", "[D&O]", "[MM]", "[", "]", "[FC]", "[CF]", "LinkZz", "[DFBC]", "@New_Movie", "@Infinite_Movies2", "MM", "@R A R B G", "[F&T]", "[KMH]", "[DnO]", "[F&T]", "MLM", "@TM_LMO", "@x265_E4E", "@HEVC MoviesZ", "SSDMovies", "@MM Linkz", "[CC]", "@Mallu_Movies", "@DK Drama", "@luxmv_Linkz", "@Akw_links", "CK HEVC", "@Team_HDT", "[CP]", "www 1TamilMV men", "www TamilRockers", "@MM", "@mm", "[MW]", "@TN68 Linkzz", "@Clipmate_Movie", "[MASHOBUC]", "Official TheMoviesBoss", "www CineVez one", "www 7MovieRulz lv", "www 1TamilMV vip", "[SMM Official]", "[Movie Bazar]", "@BM_Links", "[CG]", "Filmy4wap xyz", "www 1TamilMV pw", "www TamilBlasters pm", "[FH]", "Torrent911 tv", "[MZM]", "www CineVez top", "www CineVez top", "www 7MovieRulz sx", "[YDF]", "www 1TamilMV art", "www TamilBlasters me", "[mwkOTT]", "@Tamil_LinkzZ", "[LV]", "@The_4x_Team", "TheMoviesBoss"]

async def spell_words(string):
    prohibitedWords = SPELL_WORDS
    big_regex = re.compile(r'(\s?(' + '|'.join(map(re.escape, prohibitedWords)) + r')\b\s?)|(\s?\b(' + '|'.join(map(re.escape, prohibitedWords)) + r')\s?)')
    formatted = big_regex.sub(lambda match: match.group().replace(match.group(2) or match.group(4), ""), string)
    return formatted.replace("-"," ")	

	        
def replace_username(text):
    prohibited_words = BLACKLIST_WORDS
    big_regex = re.compile('|'.join(map(re.escape, prohibited_words)))
    text = big_regex.sub("", text)

    # Remove usernames
    usernames = re.findall("([@][A-Za-z0-9_]+)", text)
    for username in usernames:
        text = text.replace(username, "")

    # Remove emojis
    text = ''.join(char for char in text if unicodedata.category(char) != 'So')

    # Remove multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()

    return text




logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


client = AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(mongo_name='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)
    chat_id = fields.StrField(allow_none=True)
    msg_id = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name',)
        collection_name = COLLECTION_NAME


async def save_file(bot, media):
    """Save file in database"""

    try:
        file_id, file_ref = unpack_new_file_id(media.file_id)
        file_name = re.sub(r"[_\-.+]", " ", str(media.file_name))
        
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )
        await file.commit()
        
        logger.info(f'{file_name} is saved to database')
        return True, 1
        
    except ValidationError as e:
        logger.exception('Error occurred while saving file in database')
        return False, 2
    
    except DuplicateKeyError:
        logger.warning(f'{getattr(media, "file_name", "NO_FILE")} is already saved in database')
        return False, 0


TMDB_API_KEY = 'c6696789336deec34d585a64b4bbfa18'

FONT_URL = "https://github.com/Anshvachhani99/resources/raw/main/Roboto-Bold.ttf?raw=true"


def fetch_font(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses
        return BytesIO(response.content)
    except Exception as e:
        print(f"Error fetching font: {e}")
        return None

def add_watermark(image, watermark_text=" Visit @Request_Movies_V2 "):
    try:
        # Initialize ImageDraw
        draw = ImageDraw.Draw(image)
        
        # Fetch and load the font
        font_bytes = fetch_font(FONT_URL)
        if font_bytes is None:
            font = ImageFont.load_default()  # Fallback to default font if custom font fails
        else:
            font = ImageFont.truetype(font_bytes, 35)  # Adjust size as needed

        # Calculate text size and bounding box
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Ensure padding is within image dimensions
        rect_x1 = (image.width - text_width - 10) // 2
        rect_y1 = image.height - text_height - 50
        rect_x2 = rect_x1 + text_width + 10
        rect_y2 = rect_y1 + text_height + 10
        
        # Draw rounded rectangle
        draw.rounded_rectangle([rect_x1, rect_y1, rect_x2, rect_y2],
                               fill=(255, 255, 255, 200), radius=9)
        
        # Calculate position for the text
        text_x = rect_x1 + (rect_x2 - rect_x1 - text_width) // 2
        text_y = rect_y1 + (rect_y2 - rect_y1 - text_height) // 2
        
        # Draw text
        draw.text((text_x, text_y), watermark_text, fill=(0, 0, 0), font=font)

        return image
    except Exception as e:
        print(f"Error adding watermark: {e}")
        return image


def search_backdrop(name, year=None):
    try:
        # Search for movies first
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={name}"
        search_response = requests.get(search_url)
        search_data = search_response.json()

        if search_data['results']:
            # Filter results by year if provided
            if year:
                for movie in search_data['results']:
                    if movie.get('release_date', '').startswith(year):
                        movie_id = movie['id']
                        backdrop_path = movie.get('backdrop_path')
                        break
                else:
                    movie_id = None
                    backdrop_path = None
            else:
                # Return the most relevant result (first one) if no year is provided
                movie = search_data['results'][0]
                movie_id = movie['id']
                backdrop_path = movie.get('backdrop_path')

            if movie_id:
                # Fetch movie details to get the backdrop path
                details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
                details_response = requests.get(details_url)
                details_data = details_response.json()

                backdrop_path = details_data.get('backdrop_path')
                backdrop_url = f"https://image.tmdb.org/t/p/w780{backdrop_path}" if backdrop_path else None

                if backdrop_url:
                    # Add watermark to the image
                    image_response = requests.get(backdrop_url)
                    image = Image.open(BytesIO(image_response.content))
                    image = add_watermark(image, "  Visit @Request_Movies_V2  ")

                    output = BytesIO()
                    image.save(output, format='PNG')
                    output.seek(0)

                    return {
                        'title': details_data.get('title'),
                        'year': details_data.get('release_date', '').split('-')[0],
                        'genres': [genre['name'] for genre in details_data.get('genres', [])],
                        'backdrop_image': output
                    }

        # If no movie backdrop is found, search for TV shows
        search_url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={name}"
        search_response = requests.get(search_url)
        search_data = search_response.json()

        if search_data['results']:
            # Filter results by year if provided
            if year:
                for tv in search_data['results']:
                    if tv.get('first_air_date', '').startswith(year):
                        tv_id = tv['id']
                        backdrop_path = tv.get('backdrop_path')
                        break
                else:
                    tv_id = None
                    backdrop_path = None
            else:
                # Return the most relevant result (first one) if no year is provided
                tv = search_data['results'][0]
                tv_id = tv['id']
                backdrop_path = tv.get('backdrop_path')

            if tv_id:
                # Fetch TV show details to get the backdrop path
                details_url = f"https://api.themoviedb.org/3/tv/{tv_id}?api_key={TMDB_API_KEY}"
                details_response = requests.get(details_url)
                details_data = details_response.json()

                backdrop_path = details_data.get('backdrop_path')
                backdrop_url = f"https://image.tmdb.org/t/p/w780{backdrop_path}" if backdrop_path else None

                if backdrop_url:
                    # Add watermark to the image
                    image_response = requests.get(backdrop_url)
                    image = Image.open(BytesIO(image_response.content))
                    image = add_watermark(image, "  Visit @Request_Movies_V2  ")

                    output = BytesIO()
                    image.save(output, format='PNG')
                    output.seek(0)

                    return {
                        'title': details_data.get('name'),
                        'year': details_data.get('first_air_date', '').split('-')[0],
                        'genres': [genre['name'] for genre in details_data.get('genres', [])],
                        'backdrop_image': output
                    }

        return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

CAPTION_LANGUAGES = ["English", "Hindi", "Spanish", "French", "German", "Chinese", "Arabic", 
                     "Portuguese", "Russian", "Japanese", "Gujarati", "Marathi", "Tamil", "Telugu",
                     "Bengali", "Punjabi", "Kannada", "Malayalam", "Odia", "Assamese", "Urdu"]

CAPTION_QUALITY = ["HDCAM", "HQ", "HDRip", "WEB-DL", "CAMRip", "HDTC", "PreDVD", 
                   "DVDScr", "DVDRip", "DVDScreen", "HDTS", "HDR10", "Blu-ray", "4K",
                   "WebRip", "WEB", "HD", "SD", "TS", "DTH", "HDTV"]

season_episode_pattern = re.compile(r"(S\d{2}E\d{2}|S\d{2}|E\d{2}|s\d{2})", re.IGNORECASE)

year_pattern = re.compile(r"\b(19|20)\d{2}\b")

async def send_msg(bot, filename, caption):        
    year_match = year_pattern.search(caption)
    year = year_match.group(0) if year_match else None

    # Process the filename based on the year or season/episode indicator
    filename = filename[:filename.find(year) + 4] if year else (
        filename[:season_episode_pattern.search(filename).start()].strip() if season_episode_pattern.search(filename) else filename
    )
    # Clean up the filename by removing unwanted characters and replacing _ and - with spaces
    filename = re.sub(r"[()\[\]{}:;'!\"+]", "", filename)  # Remove specific special characters
    filename = re.sub(r"[-_]+", " ", filename)  # Replace hyphens and underscores with spaces
    filename = re.sub(r"\s+", " ", filename).strip()  # Remove extra spaces

    # Check if the filename already exists in the database
    if await top.is_filename_present(filename):
        logging.info(f'{filename} already exists in the database. Skipping sending.')
        return  # Exit the function early to avoid sending duplicate messages

    quality = await get_qualities(caption.lower(), CAPTION_QUALITY) or "Unknown"    
    language = ", ".join(lang for lang in CAPTION_LANGUAGES if lang.lower() in caption.lower()) or "None"

    user_id = 5660839376
    try:
        if await top.add_name(user_id, filename):
            logging.info(f'{filename} added to the database.')
            
            # Extract name from the caption
            match = re.match(r'(.+?)\s*(\d{4})$', filename)
            if match:
                name = match.group(1).strip()
                year = match.group(2)
            else:
                name = filename
                year = None
            
            # Search for the backdrop
            backdrop_data = search_backdrop(name, year=year)
            
            if backdrop_data:
                filenames = replace_username(filename).replace(" ", '-')
                button = InlineKeyboardButton('Get File 📁', url=f"https://t.me/{temp.U_NAME}?start=getfile-{filenames}")
                keyboard = InlineKeyboardMarkup([[button]])
                new_caption = f"`{backdrop_data['title']}` ✅\n\n<b>📆 Year - {backdrop_data['year']}</b>\n<b>🎥 Genre - {', '.join(backdrop_data['genres'])}</b>\n<b>📀 Format - {quality}</b>\n<b>🔊 Audio - {language}</b>"              
                await bot.send_photo(7298944577, photo=backdrop_data['backdrop_image'], caption=new_caption, reply_markup=keyboard)
            else:
                # Create an inline keyboard with a "Get File 📁" button
                filenames = replace_username(filename).replace(" ", '-')
                button = InlineKeyboardButton('Get File 📁', url=f"https://t.me/{temp.U_NAME}?start=getfile-{filenames}")
                keyboard = InlineKeyboardMarkup([[button]])
                
                # Send the original caption with the file button
                await bot.send_message(7298944577, text=f"{filenames}", reply_markup=keyboard)
        else:
            logging.error(f'Failed to add {filename} to the database.')
    except pymongo.errors.DuplicateKeyError:
        logging.warning(f'{filename} already exists in the database. Skipping insertion.')

    
async def get_qualities(text, qualities: list):
    """Get all Quality from text"""
    quality_matches = [q for q in qualities if q.lower() in text]
    return ", ".join(quality_matches) if quality_matches else "Unknown"

async def get_search_results(query, file_type=None, max_results=8, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()
    #if filter:
        #better ?
        #query = query.replace(' ', r'(\s|\.|\+|\-|_)')
        #raw_pattern = r'(\s|_|\-|\.|\+)' + query + r'(\s|_|\-|\.|\+)'
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_()]')        
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ''

    cursor = Media.find(filter)
    # Sort by recent
    cursor.sort('$natural', -1)
    # Slice files according to offset and max results
    cursor.skip(offset).limit(max_results)
    # Get list of files
    files = await cursor.to_list(length=max_results)

    return files, next_offset, total_results

async def get_bad_files(query, file_type=None, max_results=1000, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()
    #if filter:
        #better ?
        #query = query.replace(' ', r'(\s|\.|\+|\-|_)')
        #raw_pattern = r'(\s|_|\-|\.|\+)' + query + r'(\s|_|\-|\.|\+)'
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ''

    cursor = Media.find(filter)
    # Sort by recent
    cursor.sort('$natural', -1)
    # Slice files according to offset and max results
    cursor.skip(offset).limit(max_results)
    # Get list of files
    files = await cursor.to_list(length=max_results)

    return files, next_offset, total_results

async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
