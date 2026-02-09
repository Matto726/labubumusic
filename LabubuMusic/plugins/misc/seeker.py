import asyncio
from LabubuMusic.misc import db
from LabubuMusic.utils.database import get_active_chats, is_music_playing

async def update_played_duration():
    """Background task to update the played duration of tracks."""
    while True:
        await asyncio.sleep(1)
        
        try:
            active_list = await get_active_chats()
            
            for chat_id in active_list:
                if not await is_music_playing(chat_id):
                    continue
                
                track_data = db.get(chat_id)
                if not track_data:
                    continue
                
                current_track = track_data[0]
                total_duration = int(current_track.get("seconds", 0))
                
                if total_duration == 0:
                    continue
                
                current_pos = current_track.get("played", 0)
                
                if current_pos >= total_duration:
                    continue

                db[chat_id][0]["played"] = current_pos + 1
        except:
            continue

asyncio.create_task(update_played_duration())