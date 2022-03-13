# iFilmsBotz

import os
import logging
import random
import asyncio
from script import Script
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, CUSTOM_FILE_CAPTION, UPDATES, SUPPORT
from utils import get_size, is_subscribed, temp
import re
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start"))
async def start(client, message):
    if message.chat.type in ['group', 'supergroup']:
        buttons = [
            [
                InlineKeyboardButton('🤖 Updates', url='https://t.me/{UPDATES}')
            ],
            [
                InlineKeyboardButton('ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help"),
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(Script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), disable_web_page_preview=True, reply_markup=reply_markup)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, Script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, Script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('📢 Uᴘᴅᴀᴛᴇs', url=f'https://t.me/{UPDATES}'),
            InlineKeyboardButton('🎻 Sᴜᴘᴘᴏʀᴛ', url=f'https://t.me/{SUPPORT}')
            ],[
            InlineKeyboardButton('📚 Hᴇʟᴘ', callback_data='help'), 
            InlineKeyboardButton('📌 Aʙᴏᴜᴛ', callback_data='about')
            ],[
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data'), 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=Script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            quote=True,
            parse_mode='html'
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        btn = [
            [
                InlineKeyboardButton(
                    "📢 Jᴏɪɴ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ!", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            btn.append([InlineKeyboardButton("🔄 Tʀʏ Aɢᴀɪɴ!", callback_data=f"checksub#{message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**Hᴇʏ...🙋‍♂ Pʟᴇᴀsᴇ Jᴏɪɴ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ Tᴏ Usᴇ Tʜɪs Bᴏᴛ! ❤️‍🔥**",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode="markdown"
            )
        await client.send_message(LOG_CHANNEL, Script.NOT_SUBSCRIBED_TXT.format(message.from_user.id, message.from_user.mention, message.text)
            )
        return
 
    if len(message.command) ==2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('📢 Uᴘᴅᴀᴛᴇs', url=f'https://t.me/{UPDATES}'),
            InlineKeyboardButton('🎻 Sᴜᴘᴘᴏʀᴛ', url=f'https://t.me/{SUPPORT}')
            ],[
            InlineKeyboardButton('📚 Hᴇʟᴘ', callback_data='help'), 
            InlineKeyboardButton('📌 Aʙᴏᴜᴛ', callback_data='about')
            ],[
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data'), 
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=Script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            quote=True,
            parse_mode='html'
        )
        return
    file_id = message.command[1]
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply('No such file exist.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    buttons = [
        [
            InlineKeyboardButton('📢 Jᴏɪɴ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ!', url=f'https://t.me/{UPDATES}'),
        ],
        [
            InlineKeyboardButton('🎻 Sᴜᴘᴘᴏʀᴛ', url=f'https://t.me/{SUPPORT}'),
        ]
        ]
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        reply_markup=InlineKeyboardMarkup(buttons)
        )
    await client.send_message(LOG_CHANNEL, Script.FILE_TAKEN_TXT.format(message.from_user.id, message.from_user.mention, message.text))
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete File From Database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply To File With /delete Which You Want To Delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This Is Not Supported File Format')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File Is Successfully Deleted From Database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_one({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('File Is Successfully Deleted From Database')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_one({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File Is Successfully Deleted From Database')
            else:
                await msg.edit('File Not Found In Database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This Will Delete All Indexed Files.\nDo You Want To Continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="ʏᴇs ✓", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="ᴄʟᴏsᴇ ✗", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer()
    await message.message.edit('Succesfully Deleted All The Indexed Files.')

@Client.on_message(filters.command('roll') & filters.incoming &~ filters.edited)
async def game_dice(bot, msg):
    try:
        await bot.send_dice(
            chat_id = msg.chat.id,
            emoji = '🎲',
            reply_to_message_id = msg.message_id
        )
    except Exception:
        pass
        
@Client.on_message(filters.command('football') & filters.incoming &~ filters.edited)
async def game_football(bot, msg):
    try:
        await bot.send_dice(
            chat_id = msg.chat.id,
            emoji = '⚽️',
            reply_to_message_id = msg.message_id
        )
    except Exception:
        pass

@Client.on_message(filters.command('basketball') & filters.incoming &~ filters.edited)
async def game_basketball(bot, msg):
    try:
        await bot.send_dice(
            chat_id = msg.chat.id,
            emoji = '🏀',
            reply_to_message_id = msg.message_id
        )
    except Exception:
        pass

@Client.on_message(filters.command('throw') & filters.incoming &~ filters.edited)
async def game_dart(bot, msg):
    try:
        await bot.send_dice(
            chat_id = msg.chat.id,
            emoji = '🎯',
            reply_to_message_id = msg.message_id
        )
    except Exception:
        pass

@Client.on_message(filters.command('luck') & filters.incoming &~ filters.edited)
async def game_luck(bot, msg):
    try:
        await bot.send_dice(
            chat_id = msg.chat.id,
            emoji = '🎰',
            reply_to_message_id = msg.message_id
        )
    except Exception:
        pass


@Client.on_message(filters.command('bowling') & filters.incoming &~ filters.edited)
async def game_bowling(bot, msg):
    try:
        await bot.send_dice(
            chat_id = msg.chat.id,
            emoji = '🎳',
            reply_to_message_id = msg.message_id
        )
    except Exception:
        pass
   
