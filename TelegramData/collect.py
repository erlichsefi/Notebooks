import configparser
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
from telethon import functions, types
import json

# Reading Configs
config = configparser.ConfigParser()
config.read("./TelegramData/config.ini")

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
# (1) Use your own values here
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

# (2) Create the client and connect
phone = config['Telegram']['phone']
username = config['Telegram']['username']
client = TelegramClient(username, api_id, api_hash)


def extract_unique_words(data):
    import re
    
    unique_words = set()
    for category, items in data.items():
        for item in items:
            title = item.get('title', '')
            words = re.findall(r'\b\w+\b', title, re.UNICODE)
            unique_words.update(words)
    return unique_words - set(category)

async def collect(results, searchs):
    for search in searchs:
        results[search] = await main_on_file(search)
    return results

async def main(searchs):
    
    terms = searchs
    results = {}
    while len(terms) != 0:
        print(f"Searching {len(terms)} Terms")
        results =  await collect(results, terms)
        terms = extract_unique_words(results)

        with open("results.json","w",encoding="utf-8") as jsonfile:
            json.dump(results,jsonfile, ensure_ascii=False)

async def main_on_file(search):
    await client.start()
    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    result = await client(functions.contacts.SearchRequest(
        q=search,
        limit=100
    ))
    
    response  = []
    for chat in result.chats:
        response.append({
            "id":chat.id,
            "title":chat.title,
            "participants_count":chat.participants_count
        })

    return response

with client:
    terms = [
            "אלי אקפרס",
             "אייבי",
             "מוצרים",
             "הנחה",
             "חינם",
             "קניות",
             "עליאקספרס",
             "אחי, זול מבצעים שווים בארץ ובחול",
             "אמזון",
             "סודיים"
            ]
    client.loop.run_until_complete(main(terms))