import sys
import os
import logging
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# ----------------------------------------------------------------------
# 🔧 Compatibility Fix for urllib3 v2.0+ and python-telegram-bot v13.x
# ----------------------------------------------------------------------
try:
    import urllib3.contrib
except ImportError:
    import urllib3
    sys.modules['urllib3.contrib.appengine'] = None

# ----------------------------------------------------------------------
# 🔑 Configuration and Global Variables
# ----------------------------------------------------------------------
TELEGRAM_TOKEN = "8372096628:AAGOX8iH-FywcwuKskc6upo7A6AhQ1Yxss0"
BASE_URL = "https://hentaifox.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Callback Data Prefixes
MANGA_PREFIX = "M_"
DOWNLOAD_PREFIX = "D_"
PAGE_PREFIX = "P_"
BACK_TO_LIST = "BACK_LIST"
BACK_TO_START = "BACK_START"

# ----------------------------------------------------------------------
# 🔍 Scraping Logic
# ----------------------------------------------------------------------

def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def fetch_manga_list(search_path):
    results = []
    seen_urls = set()
    # Fetch 2 pages to have enough for pagination (roughly 40 items)
    for page in range(1, 7): 
        url = f"{BASE_URL}{search_path}&pag={page}" if "search" in search_path else f"{BASE_URL}{search_path}pag/{page}/"
        soup = get_soup(url)
        if not soup: break
        gallery_container = soup.find('div', class_='lc_galleries')
        if not gallery_container: break
        items = gallery_container.find_all('div', class_='thumb')
        if not items: break

        for item in items:
            caption_div = item.find('div', class_='caption')
            title_tag = caption_div.find('a') if caption_div else None
            title = title_tag.get_text(strip=True) if title_tag else "Unknown"
            link = title_tag['href'].split('/gallery/')[-1].strip('/') if title_tag else None
            
            # Extract Cover Image
            img_tag = item.find('img')
            cover_url = ""
            if img_tag:
                cover_url = img_tag.get('data-src') or img_tag.get('src')
                if cover_url and cover_url.startswith('//'):
                    cover_url = 'https:' + cover_url
            
            if link and link not in seen_urls:
                seen_urls.add(link)
                results.append({'title': title[:70], 'id': link, 'cover': cover_url})
        if len(items) < 15: break
    return results

def get_gallery_details(manga_id):
    url = f"{BASE_URL}/gallery/{manga_id}/"
    soup = get_soup(url)
    if not soup: return None
    
    load_pages_input = soup.find('input', {'id': 'load_pages'})
    info_div = soup.find('div', class_='info')
    title = info_div.find('h1').get_text(strip=True) if info_div else "Manga"
    
    # Get cover from detail page if needed
    cover_div = soup.find('div', class_='cover')
    cover_url = ""
    if cover_div and cover_div.find('img'):
        img = cover_div.find('img')
        cover_url = img.get('data-src') or img.get('src')
        if cover_url and cover_url.startswith('//'): cover_url = 'https:' + cover_url

    if load_pages_input:
        total_pages = int(load_pages_input['value'])
        thumb_img = soup.find('img', class_='lazy preloader')
        base_img_url = ""
        if thumb_img and 'data-src' in thumb_img.attrs:
            thumb_src = thumb_img['data-src']
            parts = thumb_src.split('/')
            base_img_url = "/".join(parts[:-1]) + "/"
        
        return {
            'title': title, 'total_pages': total_pages,
            'base_url': base_img_url, 'gallery_url': url,
            'id': manga_id, 'cover': cover_url
        }
    return None

def create_pdf(details):
    images = []
    session = requests.Session()
    session.headers.update(HEADERS)
    session.headers.update({'Referer': details['gallery_url']})
    for i in range(1, details['total_pages'] + 1):
        for ext in ['jpg', 'png', 'webp']:
            img_url = f"{details['base_url']}{i}.{ext}"
            try:
                r = session.get(img_url, timeout=10)
                if r.status_code == 200:
                    img = Image.open(BytesIO(r.content))
                    if img.mode != 'RGB': img = img.convert('RGB')
                    images.append(img)
                    break
            except: continue
    if images:
        safe_title = "".join([c for c in details['title'] if c.isalnum() or c in (' ', '-', '_')]).strip()[:50]
        pdf_path = f"{safe_title}.pdf"
        images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:])
        return pdf_path
    return None

# ----------------------------------------------------------------------
# 🤖 Telegram Bot Handlers
# ----------------------------------------------------------------------

def start(update: Update, context: CallbackContext) -> None:
    welcome_text = (
        "👋 *Welcome to Manga Downloader Bot!*\n\n"
        "Commands:\n"
        "🔍 `/search <name>` - Search by name\n"
        "🏷 `/tag <tag>` - Search by tag"
    )
    if update.callback_query:
        update.callback_query.message.edit_text(welcome_text, parse_mode='Markdown')
    else:
        update.message.reply_text(welcome_text, parse_mode='Markdown')

def search_command(update: Update, context: CallbackContext) -> None:
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("❌ Example: `/search isekai`", parse_mode='Markdown')
        return
    results = fetch_manga_list(f"/search/?q={query}")
    handle_search_results(update, context, results)

def tag_command(update: Update, context: CallbackContext) -> None:
    tag = " ".join(context.args).lower().replace(" ", "-")
    if not tag:
        update.message.reply_text("❌ Example: `/tag isekai`", parse_mode='Markdown')
        return
    results = fetch_manga_list(f"/tag/{tag}/")
    handle_search_results(update, context, results)

def handle_search_results(update, context, results):
    if not results:
        update.effective_message.reply_text("😔 No results found.")
        return
    context.user_data['results'] = results
    context.user_data['page'] = 0
    send_paged_results(update.effective_message, context)

def send_paged_results(message, context):
    results = context.user_data.get('results', [])
    page = context.user_data.get('page', 0)
    page_size = 10
    start_idx = page * page_size
    end_idx = start_idx + page_size
    
    current_batch = results[start_idx:end_idx]
    keyboard = []
    for item in current_batch:
        keyboard.append([InlineKeyboardButton(item['title'], callback_data=f"{MANGA_PREFIX}{item['id']}")])
    
    # Navigation row
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"{PAGE_PREFIX}prev"))
    if end_idx < len(results):
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"{PAGE_PREFIX}next"))
    if nav_row: keyboard.append(nav_row)
    
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data=BACK_TO_START)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"📚 *Results (Page {page + 1})*\nSelect a manga:"
    
    try:
        message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    except:
        message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    query.answer()

    if data == BACK_TO_START:
        start(update, context)
    elif data == BACK_TO_LIST:
        send_paged_results(query.message, context)
    elif data.startswith(PAGE_PREFIX):
        action = data.replace(PAGE_PREFIX, "")
        if action == "next": context.user_data['page'] += 1
        else: context.user_data['page'] -= 1
        send_paged_results(query.message, context)

    elif data.startswith(MANGA_PREFIX):
        manga_id = data.replace(MANGA_PREFIX, "")
        details = get_gallery_details(manga_id)
        if details:
            text = f"📖 *{details['title']}*\n📄 Pages: {details['total_pages']}"
            keyboard = [
                [InlineKeyboardButton("📥 Download PDF", callback_data=f"{DOWNLOAD_PREFIX}{manga_id}")],
                [InlineKeyboardButton("⬅️ Back to List", callback_data=BACK_TO_LIST)]
            ]
            # Delete old message and send photo with caption
            query.message.delete()
            if details['cover']:
                context.bot.send_photo(chat_id=chat_id, photo=details['cover'], caption=text, 
                                     reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            else:
                context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        else:
            query.edit_message_text("❌ Error fetching details.")

    elif data.startswith(DOWNLOAD_PREFIX):
        manga_id = data.replace(DOWNLOAD_PREFIX, "")
        details = get_gallery_details(manga_id)
        status_msg = context.bot.send_message(chat_id=chat_id, text=f"⏳ Generating PDF for *{details['title']}*...", parse_mode='Markdown')
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
        
        pdf_path = create_pdf(details)
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                context.bot.send_document(chat_id=chat_id, document=f, caption=f"✅ {details['title']}")
            os.remove(pdf_path)
            status_msg.delete()
        else:
            status_msg.edit_text("❌ Failed to generate PDF.")

def main() -> None:
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("search", search_command))
    dp.add_handler(CommandHandler("tag", tag_command))
    dp.add_handler(CallbackQueryHandler(button_handler))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()