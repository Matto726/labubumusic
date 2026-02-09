from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
)
from py_yt import VideosSearch
from LabubuMusic import matto_bot
from LabubuMusic.utils.inlinequery import answer
from config import BANNED_USERS

@matto_bot.on_inline_query(~BANNED_USERS)
async def search_inline(client, q_event):
    search_term = q_event.query.strip().lower()
    results_list = []

    if not search_term:
        try:
            return await client.answer_inline_query(q_event.id, results=answer, cache_time=10)
        except:
            return

    search_obj = VideosSearch(search_term, limit=20)
    data = (await search_obj.next()).get("result")
    
    for i in range(min(15, len(data))):
        item = data[i]
        vid_title = item["title"].title()
        vid_dur = item["duration"]
        vid_views = item["viewCount"]["short"]
        vid_thumb = item["thumbnails"][0]["url"].split("?")[0]
        chan_link = item["channel"]["link"]
        chan_name = item["channel"]["name"]
        vid_link = item["link"]
        pub_date = item["publishedTime"]
        
        desc = f"{vid_views} | {vid_dur} Min | {chan_name} | {pub_date}"
        
        btn_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="YouTube 🎄", url=vid_link)
        ]])
        
        caption_content = (
            f"❄ <b>Title:</b> <a href={vid_link}>{vid_title}</a>\n\n"
            f"⏳ <b>Duration:</b> {vid_dur} Minutes\n"
            f"👀 <b>Views:</b> <code>{vid_views}</code>\n"
            f"🎥 <b>Channel:</b> <a href={chan_link}>{chan_name}</a>\n"
            f"⏰ <b>Published:</b> {pub_date}\n\n"
            f"<u><b>➻ Inline Search Mode By {matto_bot.name}</b></u>"
        )
        
        results_list.append(
            InlineQueryResultPhoto(
                photo_url=vid_thumb,
                title=vid_title,
                thumb_url=vid_thumb,
                description=desc,
                caption=caption_content,
                reply_markup=btn_markup,
            )
        )

    try:
        await client.answer_inline_query(q_event.id, results=results_list)
    except:
        pass