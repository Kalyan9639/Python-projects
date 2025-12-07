# import telegram
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
# from bs4 import BeautifulSoup
# from PIL import Image
# import requests
# import os
# import logging
# import sys
# from io import BytesIO

# # ----------------------------------------------------------------------
# # 🔑 Configuration and Global Variables
# # ----------------------------------------------------------------------

# # ❗ BOT TOKEN INTEGRATED HERE
# TELEGRAM_TOKEN = "8530089767:AAHN7sFPH1n7M8YF9q4GSB2DDuQ1ZGzuSx8" 

# # Scraping Configuration
# BASE_URL = "https://hentai20.io/"
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#     "Referer": "https://hentai20.io/"
# }

# # Setup Logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Constants for callback data prefixes
# MANGA_PREFIX = "MANGA_"
# CHAPTER_PREFIX = "CHAPTER_"


# # ----------------------------------------------------------------------
# # 🕸️ Web Scraping Functions
# # ----------------------------------------------------------------------

# def get_soup(url):
#     """Helper function to get BeautifulSoup object from URL."""
#     try:
#         response = requests.get(url, headers=HEADERS, timeout=15)
#         response.raise_for_status()
#         return BeautifulSoup(response.text, 'html.parser')
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error fetching URL '{url}': {e}")
#         return None

# def search_manga(query):
#     """Searches for manga and returns a list of dictionaries."""
#     search_url = f"{BASE_URL}?s={query.replace(' ', '+')}"
    
#     soup = get_soup(search_url)
#     if not soup:
#         return []

#     results = []
#     # Selector based on your search_results.html analysis
#     containers = soup.select('.bsx a')
    
#     for item in containers:
#         title = item.get('title')
#         link = item.get('href')
#         if title and link:
#             results.append({'title': title, 'link': link})
            
#     return results

# def get_chapters(manga_url):
#     """Fetches available chapters, reverses the list for ascending order."""
#     soup = get_soup(manga_url)
#     if not soup:
#         return []

#     chapters = []
#     # Combined selectors for chapter list
#     chapter_list = soup.select('#chapterlist ul li a, .clstyle li a')

#     for item in chapter_list:
#         chap_title = item.find('span', class_='chapternum')
#         name = chap_title.text.strip() if chap_title else item.text.strip()
#         link = item.get('href')
        
#         if name and link:
#             chapters.append({'name': name, 'link': link})

#     # 🔑 IMPORTANT: Reverse the list to display chapters in ascending order
#     chapters.reverse() 

#     return chapters

# def download_chapter(chapter_url, manga_title, chapter_name):
#     """
#     Downloads images, combines them into a single PDF, and returns the path.
#     """
#     soup = get_soup(chapter_url)
#     if not soup:
#         return None

#     # Create safe directory names and file path
#     safe_manga_title = "".join([c for c in manga_title if c.isalnum() or c==' ']).strip()
#     safe_chapter_name = "".join([c for c in chapter_name if c.isalnum() or c==' ' or c=='-']).strip()
    
#     pdf_dir = os.path.join("Downloads", safe_manga_title)
#     os.makedirs(pdf_dir, exist_ok=True)
    
#     pdf_filename = f"{safe_chapter_name}.pdf"
#     pdf_path = os.path.join(pdf_dir, pdf_filename)
    
#     if os.path.exists(pdf_path):
#         logger.info(f"File already exists: {pdf_path}")
#         return pdf_path

#     logger.info(f"Starting download for {chapter_name}...")
#     pil_images = []
#     images = soup.select('#readerarea img')
    
#     if not images:
#         logger.warning("No images found for chapter.")
#         return None

#     for i, img in enumerate(images, 1):
#         # Fallback for data-src if src is missing (lazy loading)
#         src = img.get('src') or img.get('data-src') 
        
#         if src and src.startswith(('http', 'https')):
#             try:
#                 img_response = requests.get(src, headers=HEADERS, timeout=10)
#                 img_response.raise_for_status()
                
#                 # Load image directly from memory using BytesIO
#                 pil_image = Image.open(BytesIO(img_response.content)).convert('RGB')
#                 pil_images.append(pil_image)
#             except Exception as e:
#                 logger.error(f"Failed to process image {i} from {src}: {e}")

#     if pil_images:
#         first_image = pil_images[0]
#         rest_of_images = pil_images[1:]
        
#         try:
#             # Save all images as a single multi-page PDF
#             first_image.save(
#                 pdf_path, 
#                 "PDF", 
#                 resolution=100.0, 
#                 save_all=True, 
#                 append_images=rest_of_images
#             )
#             logger.info(f"PDF successfully created at {pdf_path}")
#             return pdf_path
#         except Exception as e:
#             logger.error(f"Failed to save PDF: {e}")
#             return None
#     else:
#         logger.warning("Could not gather any images to convert to PDF.")
#         return None


# # ----------------------------------------------------------------------
# # 🤖 Telegram Handlers
# # ----------------------------------------------------------------------

# def start(update: Update, context: CallbackContext) -> None:
#     """Sends a welcome message when the command /start is issued."""
#     welcome_message = (
#         "👋 Welcome to the Manga Downloader Bot!\n\n"
#         "To start, use the command:\n"
#         "**/search <Manga Name>**\n\n"
#         "Example: `/search The Hole Is Open`"
#     )
#     update.message.reply_text(welcome_message)

# def search_command(update: Update, context: CallbackContext) -> None:
#     """Handles the /search command, performs scraping, and shows results."""
    
#     # Extract the search query from the command arguments
#     if not context.args:
#         update.message.reply_text("Please provide a manga name after /search.\nExample: `/search The Hole Is Open`")
#         return

#     query = " ".join(context.args)
    
#     # Send "typing..." status
#     context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    
#     results = search_manga(query)
    
#     if not results:
#         update.message.reply_text(f"❌ No manga found for the query: *{query}*.", parse_mode='Markdown')
#         return

#     # Store results in user_data for later button callback
#     context.user_data['search_results'] = results
    
#     # Create inline keyboard for results
#     keyboard = []
#     message_text = f"📚 Found {len(results)} results for *{query}*:\n\n"
    
#     for i, item in enumerate(results):
#         # Callback data format: MANGA_INDEX_TITLE_...
#         # We only need the index for lookup
#         callback_data = f"{MANGA_PREFIX}{i}" 
#         keyboard.append([InlineKeyboardButton(f"{i+1}. {item['title']}", callback_data=callback_data)])
    
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     # Edit the initial text to show the enumerated results with buttons
#     update.message.reply_text(
#         text=message_text + "Please select a title:",
#         reply_markup=reply_markup, 
#         parse_mode='Markdown'
#     )

# def button_handler(update: Update, context: CallbackContext) -> None:
#     """Handles all inline button clicks (manga selection and chapter selection)."""
    
#     query = update.callback_query
#     query.answer() # Acknowledge the button press
    
#     data = query.data
    
#     # 🔑 FIX: Get chat_id from the message associated with the query, NOT effective_chat.
#     # This is correct for python-telegram-bot V13.
#     chat_id = query.message.chat_id 
    
#     # ------------------------------------
#     # Case 1: Manga Selection (Leads to Chapter List)
#     # ------------------------------------
#     if data.startswith(MANGA_PREFIX):
#         try:
#             # Extract index of selected manga from the callback data
#             manga_index = int(data.split(MANGA_PREFIX)[1])
            
#             selected_manga = context.user_data['search_results'][manga_index]
#             manga_title = selected_manga['title']
#             manga_link = selected_manga['link']
            
#             context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
#             query.edit_message_text(text=f"Loading chapters for: *{manga_title}*...", parse_mode='Markdown')

#             chapters = get_chapters(manga_link)
            
#             if not chapters:
#                 query.edit_message_text(text=f"❌ No chapters found for *{manga_title}*.", parse_mode='Markdown')
#                 return
            
#             # Store chapters for next interaction
#             context.user_data['chapter_list'] = chapters
#             context.user_data['selected_manga_title'] = manga_title

#             # Create inline keyboard for chapters
#             chapter_keyboard = []
#             message_text = f"📖 Found {len(chapters)} chapters for *{manga_title}* (Ascending Order):\n\n"
            
#             for i, chap in enumerate(chapters):
#                 # Callback data format: CHAPTER_INDEX
#                 callback_data = f"{CHAPTER_PREFIX}{i}"
#                 chapter_keyboard.append([InlineKeyboardButton(f"{i+1}. {chap['name']}", callback_data=callback_data)])
            
#             if len(chapter_keyboard) > 64:
#                  chapter_keyboard = chapter_keyboard[:63] 
                 
#             reply_markup = InlineKeyboardMarkup(chapter_keyboard)
#             query.edit_message_text(
#                 text=message_text + "Select a chapter to download as PDF:", 
#                 reply_markup=reply_markup, 
#                 parse_mode='Markdown'
#             )
            
#         except (KeyError, IndexError, ValueError) as e:
#             logger.error(f"Error processing manga selection: {e}")
#             query.edit_message_text(text="An error occurred while retrieving chapters. Please try searching again.")

#     # ------------------------------------
#     # Case 2: Chapter Selection (Leads to PDF Download)
#     # ------------------------------------
#     elif data.startswith(CHAPTER_PREFIX):
#         try:
#             # Extract index of selected chapter
#             chapter_index = int(data.split(CHAPTER_PREFIX)[1])
            
#             chapters = context.user_data.get('chapter_list', [])
#             manga_title = context.user_data.get('selected_manga_title', 'Manga')
            
#             if not chapters or chapter_index >= len(chapters):
#                  query.edit_message_text(text="Session expired or invalid chapter selection. Please start a new search.")
#                  return
            
#             selected_chapter = chapters[chapter_index]
#             chapter_name = selected_chapter['name']
#             chapter_link = selected_chapter['link']
            
#             query.edit_message_text(text=f"⏳ Starting download and PDF creation for *{chapter_name}*...", parse_mode='Markdown')
            
#             # Send "uploading document..." status
#             context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
            
#             # Perform the download and conversion
#             pdf_path = download_chapter(chapter_link, manga_title, chapter_name)
            
#             if pdf_path and os.path.exists(pdf_path):
#                 # Send the PDF file
#                 with open(pdf_path, 'rb') as pdf_file:
#                     context.bot.send_document(
#                         chat_id=chat_id, 
#                         document=pdf_file, 
#                         caption=f"🎉 Downloaded *{chapter_name}* from *{manga_title}*.",
#                         parse_mode='Markdown'
#                     )
#                 # Cleanup: Delete the local PDF file after sending
#                 os.remove(pdf_path)
#                 query.edit_message_text(text=f"✅ *{chapter_name}* sent and local file deleted.", parse_mode='Markdown')
#             else:
#                 query.edit_message_text(text=f"❌ Failed to download or create PDF for *{chapter_name}*.", parse_mode='Markdown')

#         except (KeyError, IndexError, ValueError) as e:
#             logger.error(f"Error processing chapter selection: {e}")
#             query.edit_message_text(text="An internal error occurred during download. Please try again.")

        
# def main() -> None:
#     """Starts the bot."""
    
#     # Create the Updater and pass it your bot's token.
#     updater = Updater(TELEGRAM_TOKEN, use_context=True)

#     # Get the dispatcher to register handlers
#     dispatcher = updater.dispatcher

#     # Register handlers
#     dispatcher.add_handler(CommandHandler("start", start))
#     dispatcher.add_handler(CommandHandler("search", search_command))
    
#     # Register the handler for all inline button presses
#     dispatcher.add_handler(CallbackQueryHandler(button_handler))

#     # Start the Bot
#     updater.start_polling()

#     # Run the bot until you press Ctrl-C
#     print("Bot is running. Press Ctrl-C to stop.")
#     updater.idle()

# if __name__ == '__main__':
#     main()


# ----------------------------------------------------------------------------------------

# v02


# import telegram
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
# from bs4 import BeautifulSoup
# from PIL import Image
# import requests
# import os
# import logging
# import sys
# from io import BytesIO

# # ----------------------------------------------------------------------
# # 🔑 Configuration and Global Variables
# # ----------------------------------------------------------------------

# # ❗ BOT TOKEN INTEGRATED HERE
# TELEGRAM_TOKEN = "8530089767:AAHN7sFPH1n7M8YF9q4GSB2DDuQ1ZGzuSx8" 

# # Scraping Configuration
# BASE_URL = "https://hentai20.io/"
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#     "Referer": "https://hentai20.io/"
# }

# # Setup Logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Constants for callback data prefixes
# MANGA_PREFIX = "MANGA_"
# CHAPTER_PREFIX = "CHAPTER_"
# NAV_PREFIX = "NAV_" # Used for pagination (Next/Prev)
# PAGE_LIMIT = 20 # Max number of chapters per page


# # ----------------------------------------------------------------------
# # 🕸️ Web Scraping Functions
# # ----------------------------------------------------------------------

# def get_soup(url):
#     """Helper function to get BeautifulSoup object from URL."""
#     try:
#         response = requests.get(url, headers=HEADERS, timeout=15)
#         response.raise_for_status()
#         return BeautifulSoup(response.text, 'html.parser')
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error fetching URL '{url}': {e}")
#         return None

# def search_manga(query):
#     """Searches for manga and returns a list of dictionaries."""
#     # --- CHANGE 1: Convert query to lowercase before searching ---
#     search_url = f"{BASE_URL}?s={query.lower().replace(' ', '+')}"
    
#     soup = get_soup(search_url)
#     if not soup:
#         return []

#     results = []
#     containers = soup.select('.bsx a')
    
#     for item in containers:
#         title = item.get('title')
#         link = item.get('href')
#         if title and link:
#             results.append({'title': title, 'link': link})
            
#     return results

# def get_chapters(manga_url):
#     """Fetches available chapters, reverses the list for ascending order."""
#     # ... (function body remains the same) ...
#     soup = get_soup(manga_url)
#     if not soup:
#         return []

#     chapters = []
#     chapter_list = soup.select('#chapterlist ul li a, .clstyle li a')

#     for item in chapter_list:
#         chap_title = item.find('span', class_='chapternum')
#         name = chap_title.text.strip() if chap_title else item.text.strip()
#         link = item.get('href')
        
#         if name and link:
#             chapters.append({'name': name, 'link': link})

#     # IMPORTANT: Reverse the list to display chapters in ascending order
#     chapters.reverse() 

#     return chapters

# def download_chapter(chapter_url, manga_title, chapter_name):
#     # ... (function body remains the same) ...
#     # ... (code for downloading images, converting to PDF, and cleanup) ...
#     soup = get_soup(chapter_url)
#     if not soup:
#         return None

#     safe_manga_title = "".join([c for c in manga_title if c.isalnum() or c==' ']).strip()
#     safe_chapter_name = "".join([c for c in chapter_name if c.isalnum() or c==' ' or c=='-']).strip()
    
#     pdf_dir = os.path.join("Downloads", safe_manga_title)
#     os.makedirs(pdf_dir, exist_ok=True)
    
#     pdf_filename = f"{safe_chapter_name}.pdf"
#     pdf_path = os.path.join(pdf_dir, pdf_filename)
    
#     if os.path.exists(pdf_path):
#         logger.info(f"File already exists: {pdf_path}")
#         return pdf_path

#     logger.info(f"Starting download for {chapter_name}...")
#     pil_images = []
#     images = soup.select('#readerarea img')
    
#     if not images:
#         logger.warning("No images found for chapter.")
#         return None

#     for i, img in enumerate(images, 1):
#         src = img.get('src') or img.get('data-src') 
        
#         if src and src.startswith(('http', 'https')):
#             try:
#                 img_response = requests.get(src, headers=HEADERS, timeout=10)
#                 img_response.raise_for_status()
                
#                 pil_image = Image.open(BytesIO(img_response.content)).convert('RGB')
#                 pil_images.append(pil_image)
#             except Exception as e:
#                 logger.error(f"Failed to process image {i} from {src}: {e}")

#     if pil_images:
#         first_image = pil_images[0]
#         rest_of_images = pil_images[1:]
        
#         try:
#             first_image.save(
#                 pdf_path, 
#                 "PDF", 
#                 resolution=100.0, 
#                 save_all=True, 
#                 append_images=rest_of_images
#             )
#             logger.info(f"PDF successfully created at {pdf_path}")
#             return pdf_path
#         except Exception as e:
#             logger.error(f"Failed to save PDF: {e}")
#             return None
#     else:
#         logger.warning("Could not gather any images to convert to PDF.")
#         return None


# # ----------------------------------------------------------------------
# # 🔄 Chapter Pagination Helper
# # ----------------------------------------------------------------------

# def display_chapters_page(query, context, chat_id, manga_title, chapters, page):
#     """Slices the chapter list and displays one page with navigation buttons."""
    
#     # Calculate indices and total pages
#     start_index = page * PAGE_LIMIT
#     end_index = start_index + PAGE_LIMIT
#     total_chapters = len(chapters)
#     total_pages = (total_chapters + PAGE_LIMIT - 1) // PAGE_LIMIT
    
#     # Slice the chapters for the current page
#     chapters_on_page = chapters[start_index:end_index]
    
#     chapter_keyboard = []
    
#     message_text = f"📖 Chapters for *{manga_title}* (Page {page + 1}/{total_pages}):\n\n"
    
#     # Add chapter buttons (use ABSOLUTE index for callback data)
#     for i, chap in enumerate(chapters_on_page):
#         # We use the ABSOLUTE index (start_index + i) for the callback data
#         absolute_index = start_index + i
#         callback_data = f"{CHAPTER_PREFIX}{absolute_index}"
#         chapter_keyboard.append([InlineKeyboardButton(f"{absolute_index + 1}. {chap['name']}", callback_data=callback_data)])

#     # Add navigation buttons (Previous/Next)
#     nav_buttons = []
#     if page > 0:
#         nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"{NAV_PREFIX}{page - 1}"))

#     # Add current page number button (non-functional)
#     nav_buttons.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="ignore"))

#     if page < total_pages - 1:
#         nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{NAV_PREFIX}{page + 1}"))
    
#     if len(nav_buttons) > 1:
#         chapter_keyboard.append(nav_buttons) # Only add navigation row if it has buttons

#     # Ensure max button limit is respected
#     if len(chapter_keyboard) > 64:
#         chapter_keyboard = chapter_keyboard[:63]
    
#     reply_markup = InlineKeyboardMarkup(chapter_keyboard)
    
#     query.edit_message_text(
#         text=message_text + "Select a chapter to download as PDF:", 
#         reply_markup=reply_markup, 
#         parse_mode='Markdown'
#     )


# # ----------------------------------------------------------------------
# # 🤖 Telegram Handlers
# # ----------------------------------------------------------------------

# def start(update: Update, context: CallbackContext) -> None:
#     # ... (function body remains the same) ...
#     welcome_message = (
#         "👋 Welcome to the Manga Downloader Bot!\n\n"
#         "To start, use the command:\n"
#         "**/search <Manga Name>**\n\n"
#         "Example: `/search The Hole Is Open`"
#     )
#     update.message.reply_text(welcome_message)

# def search_command(update: Update, context: CallbackContext) -> None:
#     # ... (function body remains the same) ...
#     if not context.args:
#         update.message.reply_text("Please provide a manga name after /search.\nExample: `/search The Hole Is Open`")
#         return

#     query = " ".join(context.args)
#     context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    
#     results = search_manga(query) # search_manga now handles lowercasing
    
#     if not results:
#         update.message.reply_text(f"❌ No manga found for the query: *{query}*.", parse_mode='Markdown')
#         return

#     context.user_data['search_results'] = results
    
#     keyboard = []
#     message_text = f"📚 Found {len(results)} results for *{query}*:\n\n"
    
#     for i, item in enumerate(results):
#         callback_data = f"{MANGA_PREFIX}{i}" 
#         keyboard.append([InlineKeyboardButton(f"{i+1}. {item['title']}", callback_data=callback_data)])
    
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     update.message.reply_text(
#         text=message_text + "Please select a title:",
#         reply_markup=reply_markup, 
#         parse_mode='Markdown'
#     )

# def button_handler(update: Update, context: CallbackContext) -> None:
#     """Handles all inline button clicks, including search selection and pagination."""
    
#     query = update.callback_query
#     query.answer() 
    
#     data = query.data
    
#     # Fix for V13: Get chat_id from the message associated with the query
#     chat_id = query.message.chat_id 
    
#     # ------------------------------------
#     # Case 1: Manga Selection (MANGA_INDEX) - Initial Chapter Load
#     # ------------------------------------
#     if data.startswith(MANGA_PREFIX):
#         try:
#             manga_index = int(data.split(MANGA_PREFIX)[1])
#             selected_manga = context.user_data['search_results'][manga_index]
#             manga_title = selected_manga['title']
#             manga_link = selected_manga['link']
            
#             context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
#             query.edit_message_text(text=f"Loading chapters for: *{manga_title}*...", parse_mode='Markdown')

#             chapters = get_chapters(manga_link)
            
#             if not chapters:
#                 query.edit_message_text(text=f"❌ No chapters found for *{manga_title}*.", parse_mode='Markdown')
#                 return
            
#             # Store full chapter list for pagination
#             context.user_data['chapter_list'] = chapters
#             context.user_data['selected_manga_title'] = manga_title
            
#             # Display the first page (page 0)
#             display_chapters_page(query, context, chat_id, manga_title, chapters, page=0)
            
#         except (KeyError, IndexError, ValueError) as e:
#             logger.error(f"Error processing manga selection: {e}")
#             query.edit_message_text(text="An error occurred while retrieving chapters. Please try searching again.")

#     # ------------------------------------
#     # Case 2: Chapter Navigation (NAV_PAGE)
#     # ------------------------------------
#     elif data.startswith(NAV_PREFIX):
#         page = int(data.split(NAV_PREFIX)[1])
        
#         manga_title = context.user_data.get('selected_manga_title')
#         chapters = context.user_data.get('chapter_list')

#         if not chapters or manga_title is None:
#             query.edit_message_text(text="Session expired. Please start a new search.")
#             return

#         # Display the requested page
#         display_chapters_page(query, context, chat_id, manga_title, chapters, page)
        
#     # ------------------------------------
#     # Case 3: Chapter Selection (CHAPTER_INDEX) - Leads to PDF Download
#     # ------------------------------------
#     elif data.startswith(CHAPTER_PREFIX):
#         try:
#             # Chapter index is ABSOLUTE index (not page index)
#             chapter_index = int(data.split(CHAPTER_PREFIX)[1])
            
#             chapters = context.user_data.get('chapter_list', [])
#             manga_title = context.user_data.get('selected_manga_title', 'Manga')
            
#             if not chapters or chapter_index >= len(chapters):
#                  query.edit_message_text(text="Session expired or invalid chapter selection. Please start a new search.")
#                  return
            
#             selected_chapter = chapters[chapter_index]
#             chapter_name = selected_chapter['name']
#             chapter_link = selected_chapter['link']
            
#             query.edit_message_text(text=f"⏳ Starting download and PDF creation for *{chapter_name}*...", parse_mode='Markdown')
            
#             context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
            
#             pdf_path = download_chapter(chapter_link, manga_title, chapter_name)
            
#             if pdf_path and os.path.exists(pdf_path):
#                 with open(pdf_path, 'rb') as pdf_file:
#                     context.bot.send_document(
#                         chat_id=chat_id, 
#                         document=pdf_file, 
#                         caption=f"🎉 Downloaded *{chapter_name}* from *{manga_title}*.",
#                         parse_mode='Markdown'
#                     )
#                 os.remove(pdf_path)
#                 query.edit_message_text(text=f"✅ *{chapter_name}* sent and local file deleted.", parse_mode='Markdown')
#             else:
#                 query.edit_message_text(text=f"❌ Failed to download or create PDF for *{chapter_name}*.", parse_mode='Markdown')

#         except (KeyError, IndexError, ValueError) as e:
#             logger.error(f"Error processing chapter selection: {e}")
#             query.edit_message_text(text="An internal error occurred during download. Please try again.")


# def main() -> None:
#     """Starts the bot."""
#     # ... (function body remains the same) ...
#     updater = Updater(TELEGRAM_TOKEN, use_context=True)
#     dispatcher = updater.dispatcher

#     dispatcher.add_handler(CommandHandler("start", start))
#     dispatcher.add_handler(CommandHandler("search", search_command))
#     dispatcher.add_handler(CallbackQueryHandler(button_handler))

#     updater.start_polling()

#     print("Bot is running. Press Ctrl-C to stop.")
#     updater.idle()

# if __name__ == '__main__':
#     main()


# ------------------------------------------------------------------------------------------------

# v03


import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from bs4 import BeautifulSoup
from PIL import Image
import requests
import os
import logging
import sys
from io import BytesIO

# ----------------------------------------------------------------------
# ⚠️ Warning Suppression

import warnings

# Suppress warnings related to urllib3 trying to load AppEngine contrib
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3.contrib.appengine")


# ----------------------------------------------------------------------
# 🔑 Configuration and Global Variables
# ----------------------------------------------------------------------

# ❗ BOT TOKEN INTEGRATED HERE
TELEGRAM_TOKEN = "8530089767:AAHN7sFPH1n7M8YF9q4GSB2DDuQ1ZGzuSx8" 

# Scraping Configuration
BASE_URL = "https://hentai20.io/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://hentai20.io/"
}

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for callback data prefixes
MANGA_PREFIX = "MANGA_"
CHAPTER_PREFIX = "CHAPTER_"
NAV_PREFIX = "NAV_" 
BACK_PREFIX = "BACK_TO_SEARCH" # New constant for Back button
PAGE_LIMIT = 20 


# ----------------------------------------------------------------------
# 🕸️ Web Scraping Functions
# ----------------------------------------------------------------------

def get_soup(url):
    """Helper function to get BeautifulSoup object from URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL '{url}': {e}")
        return None

def search_manga(query):
    """Searches for manga and returns list with titles, links, and IMAGES."""
    search_url = f"{BASE_URL}?s={query.lower().replace(' ', '+')}"
    
    soup = get_soup(search_url)
    if not soup:
        return []

    results = []
    containers = soup.select('.bsx a')
    
    for item in containers:
        title = item.get('title')
        link = item.get('href')
        
        img_tag = item.select_one('img')
        image_url = img_tag.get('src') or img_tag.get('data-src') if img_tag else None

        if title and link:
            results.append({'title': title, 'link': link, 'image': image_url})
            
    return results

def get_chapters(manga_url):
    """Fetches available chapters, reverses the list for ascending order."""
    soup = get_soup(manga_url)
    if not soup:
        return []

    chapters = []
    chapter_list = soup.select('#chapterlist ul li a, .clstyle li a')

    for item in chapter_list:
        chap_title = item.find('span', class_='chapternum')
        name = chap_title.text.strip() if chap_title else item.text.strip()
        link = item.get('href')
        
        if name and link:
            chapters.append({'name': name, 'link': link})

    chapters.reverse() 
    return chapters

def download_chapter(chapter_url, manga_title, chapter_name):
    """Downloads images and combines them into a PDF."""
    soup = get_soup(chapter_url)
    if not soup:
        return None

    safe_manga_title = "".join([c for c in manga_title if c.isalnum() or c==' ']).strip()
    safe_chapter_name = "".join([c for c in chapter_name if c.isalnum() or c==' ' or c=='-']).strip()
    
    pdf_dir = os.path.join("Downloads", safe_manga_title)
    os.makedirs(pdf_dir, exist_ok=True)
    
    pdf_filename = f"{safe_chapter_name}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    if os.path.exists(pdf_path):
        return pdf_path

    logger.info(f"Starting download for {chapter_name}...")
    pil_images = []
    images = soup.select('#readerarea img')
    
    if not images:
        return None

    for i, img in enumerate(images, 1):
        src = img.get('src') or img.get('data-src') 
        
        if src and src.startswith(('http', 'https')):
            try:
                img_response = requests.get(src, headers=HEADERS, timeout=10)
                img_response.raise_for_status()
                pil_image = Image.open(BytesIO(img_response.content)).convert('RGB')
                pil_images.append(pil_image)
            except Exception as e:
                logger.error(f"Failed image {i}: {e}")

    if pil_images:
        first_image = pil_images[0]
        rest_of_images = pil_images[1:]
        try:
            first_image.save(pdf_path, "PDF", resolution=100.0, save_all=True, append_images=rest_of_images)
            return pdf_path
        except Exception as e:
            return None
    else:
        return None


# ----------------------------------------------------------------------
# 🔄 Display Helpers
# ----------------------------------------------------------------------

def show_search_results(context, chat_id, results, query_text):
    """Helper to display the list of manga (Used by /search and Back button)."""
    keyboard = []
    message_text = f"📚 Found {len(results)} results for *{query_text}*:\n\n"
    
    for i, item in enumerate(results):
        callback_data = f"{MANGA_PREFIX}{i}" 
        keyboard.append([InlineKeyboardButton(f"{i+1}. {item['title']}", callback_data=callback_data)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.send_message(
        chat_id=chat_id,
        text=message_text + "Please select a title:",
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )

def display_chapters_page(context, chat_id, manga_title, chapters, page, image_url=None, message_to_edit=None):
    """Displays a page of chapters with pagination and Back button."""
    
    start_index = page * PAGE_LIMIT
    end_index = start_index + PAGE_LIMIT
    total_chapters = len(chapters)
    total_pages = (total_chapters + PAGE_LIMIT - 1) // PAGE_LIMIT
    
    chapters_on_page = chapters[start_index:end_index]
    
    # 1. Chapter Buttons
    chapter_keyboard = []
    for i, chap in enumerate(chapters_on_page):
        absolute_index = start_index + i
        callback_data = f"{CHAPTER_PREFIX}{absolute_index}"
        chapter_keyboard.append([InlineKeyboardButton(f"{absolute_index + 1}. {chap['name']}", callback_data=callback_data)])

    # 2. Navigation Buttons (Prev | Page X/Y | Next)
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{NAV_PREFIX}{page - 1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="ignore"))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{NAV_PREFIX}{page + 1}"))
    
    if len(nav_buttons) > 1:
        chapter_keyboard.append(nav_buttons)

    # 3. Back Button (Always present)
    chapter_keyboard.append([InlineKeyboardButton("🔙 Back to Results", callback_data=BACK_PREFIX)])

    if len(chapter_keyboard) > 64:
        chapter_keyboard = chapter_keyboard[:63]
    
    reply_markup = InlineKeyboardMarkup(chapter_keyboard)
    caption_text = f"📖 *{manga_title}*\nSelect a chapter to download:"

    # --- MODE 1: SEND NEW PHOTO (First Load) ---
    if image_url:
        try:
            context.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=caption_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            # Fallback if image fails
            context.bot.send_message(
                chat_id=chat_id,
                text=f"{caption_text}\n(Image unavailable)",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    # --- MODE 2: EDIT CAPTION (Pagination) ---
    elif message_to_edit:
        try:
            message_to_edit.edit_caption(
                caption=caption_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            # If message type changed, try editing text
            message_to_edit.edit_text(
                text=caption_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )


# ----------------------------------------------------------------------
# 🤖 Telegram Handlers
# ----------------------------------------------------------------------

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("👋 Welcome! Use `/search <Manga Name>` to begin.")

def search_command(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text("Please provide a manga name.\nExample: `/search The Hole Is Open`")
        return

    query_text = " ".join(context.args)
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    
    results = search_manga(query_text)
    
    if not results:
        update.message.reply_text(f"❌ No manga found for: *{query_text}*", parse_mode='Markdown')
        return

    # Save results and the original query text for the Back button
    context.user_data['search_results'] = results
    context.user_data['last_query'] = query_text
    
    show_search_results(context, update.effective_chat.id, results, query_text)

def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer() 
    data = query.data
    chat_id = query.message.chat_id 
    
    # --- Case 1: Manga Selection (Start Chapter View) ---
    if data.startswith(MANGA_PREFIX):
        try:
            manga_index = int(data.split(MANGA_PREFIX)[1])
            selected_manga = context.user_data['search_results'][manga_index]
            manga_title = selected_manga['title']
            manga_link = selected_manga['link']
            image_url = selected_manga.get('image')
            
            # Delete "Search Results" text to transition to "Image Message"
            try:
                query.message.delete()
            except:
                pass 

            context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_PHOTO)

            chapters = get_chapters(manga_link)
            
            if not chapters:
                # If no chapters, restore the search results message
                context.bot.send_message(chat_id=chat_id, text=f"❌ No chapters found for *{manga_title}*.")
                # Optional: You could call show_search_results here again
                return
            
            context.user_data['chapter_list'] = chapters
            context.user_data['selected_manga_title'] = manga_title
            
            display_chapters_page(context, chat_id, manga_title, chapters, page=0, image_url=image_url)
            
        except Exception as e:
            logger.error(f"Error processing manga selection: {e}")
            context.bot.send_message(chat_id=chat_id, text="Error retrieving chapters.")

    # --- Case 2: Back Button (Go back to Search Results) ---
    elif data == BACK_PREFIX:
        try:
            # Delete the "Manga Cover + Chapters" message
            try:
                query.message.delete()
            except:
                pass
            
            # Retrieve saved data
            results = context.user_data.get('search_results', [])
            last_query = context.user_data.get('last_query', 'Previous Search')
            
            if results:
                show_search_results(context, chat_id, results, last_query)
            else:
                context.bot.send_message(chat_id=chat_id, text="Session expired. Please search again.")
                
        except Exception as e:
            logger.error(f"Error processing back button: {e}")

    # --- Case 3: Pagination (Edit Caption) ---
    elif data.startswith(NAV_PREFIX):
        page = int(data.split(NAV_PREFIX)[1])
        manga_title = context.user_data.get('selected_manga_title')
        chapters = context.user_data.get('chapter_list')

        if not chapters:
            query.message.reply_text("Session expired. Please search again.")
            return

        display_chapters_page(context, chat_id, manga_title, chapters, page, message_to_edit=query.message)
        
    # --- Case 4: Chapter Download ---
    elif data.startswith(CHAPTER_PREFIX):
        try:
            chapter_index = int(data.split(CHAPTER_PREFIX)[1])
            chapters = context.user_data.get('chapter_list', [])
            manga_title = context.user_data.get('selected_manga_title', 'Manga')
            
            if not chapters or chapter_index >= len(chapters):
                 query.message.reply_text("Invalid selection.")
                 return
            
            selected_chapter = chapters[chapter_index]
            chapter_name = selected_chapter['name']
            
            status_msg = query.message.reply_text(f"⏳ Downloading *{chapter_name}*...", parse_mode='Markdown')
            context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
            
            pdf_path = download_chapter(selected_chapter['link'], manga_title, chapter_name)
            
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    context.bot.send_document(
                        chat_id=chat_id, 
                        document=pdf_file, 
                        caption=f"🎉 *{manga_title}* - {chapter_name}",
                        parse_mode='Markdown'
                    )
                os.remove(pdf_path)
                status_msg.delete()
            else:
                status_msg.edit_text("❌ Download failed.")

        except Exception as e:
            logger.error(f"Error: {e}")
            query.message.reply_text("An error occurred.")

class HealthCheckHandler(BaseHTTPRequestHandler):
    """A minimal HTTP server handler to satisfy Cloud Run's health check."""
    def do_GET(self):
        # Respond 200 OK for any GET request (especially the root path)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Telegram Bot is alive and polling.')

def run_health_check_server():
    """Starts the simple HTTP server on the required Cloud Run port."""
    # Cloud Run injects the required port via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    server_address = ('0.0.0.0', port)
    
    # Use a try-except block in case the port is already in use
    try:
        httpd = HTTPServer(server_address, HealthCheckHandler)
        print(f"Starting Cloud Run HTTP check server on port {port}...")
        httpd.serve_forever()
    except Exception as e:
        # This will exit the program if the server fails to start (e.g., port issue)
        print(f"FATAL: Failed to start HTTP server: {e}")
        os._exit(1)


# --- UPDATED MAIN FUNCTION ---

def main() -> None:
    """Starts the bot and the HTTP server concurrently."""
    
    # The TELEGRAM_TOKEN should be read from os.environ.get("TELEGRAM_TOKEN") here
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable is not set. Cannot run bot.")
        
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("search", search_command))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # 1. Start the Telegram bot polling in a separate, non-blocking thread
    polling_thread = threading.Thread(target=updater.start_polling, name="PollingThread", daemon=True)
    polling_thread.start()
    print("Telegram bot polling started in background thread.")

    # 2. Run the simple HTTP server in the main thread. 
    # This thread is blocked, but the polling thread keeps the bot responsive.
    run_health_check_server()


if __name__ == '__main__':
    main()

# def main() -> None:
#     updater = Updater(TELEGRAM_TOKEN, use_context=True)
#     dispatcher = updater.dispatcher
    
#     dispatcher.add_handler(CommandHandler("start", start))
#     dispatcher.add_handler(CommandHandler("search", search_command))
#     dispatcher.add_handler(CallbackQueryHandler(button_handler))

#     updater.start_polling()
#     print("Bot is running...")
#     updater.idle()

# if __name__ == '__main__':

#     main()
