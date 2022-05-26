# iFilmsBotz

import asyncio
import re
import ast

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from script import Script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE, LOG_CHANNEL, UPDATES, SUPPORT
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import(
   del_all,
   find_filter,
   get_filters,
)
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

@Client.on_message(filters.group & filters.text & ~filters.edited & filters.incoming)
async def give_filter(client,message):
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message) 
         
@Client.on_message(filters.private & filters.text & filters.incoming)
async def pv_filter(client,message):
    await auto_filter(client, message)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):

    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(f"⚠️ 𝖧ᴇʏ, {query.from_user.first_name} ! 𝖲ᴇᴀʀᴄʜ 𝖸ᴏᴜʀ 𝖮ᴡɴ 𝖥ɪʟᴇ, 𝖣ᴏɴ'ᴛ 𝖢ʟɪᴄᴋ 𝖮ᴛʜᴇʀ𝗌 𝖱ᴇ𝗌ᴜʟᴛ𝗌 😬", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(f"⚠️ 𝖧ᴇʏ, {query.from_user.first_name} ! 𝖸ᴏᴜ Aʀᴇ U𝗌ɪɴɢ Oɴᴇ Oғ Mʏ Oʟᴅ Mᴇ𝗌𝗌ᴀɢᴇ𝗌, Sᴇɴᴅ Tʜᴇ Rᴇǫᴜᴇ𝗌ᴛ Aɢᴀɪɴ ⚠️", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"📂[{get_size(file.file_size)}] 🎥 {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("« Bᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"📃 {round(int(offset)/10)+1} / {round(total/10)}", callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [   InlineKeyboardButton(f"🗓 {round(int(offset)/10)+1} / {round(total/10)}", callback_data="pages"),
                InlineKeyboardButton("🗑", callback_data="delit"), 
                InlineKeyboardButton("Nᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    else:
        btn.append(
            [
                InlineKeyboardButton("« Bᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {round(int(offset)/10)+1} / {round(total/10)}", callback_data="pages"),
                InlineKeyboardButton("Nᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup( 
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(f"⚠️ 𝖧ᴇʏ, {query.from_user.first_name} ! 𝖲ᴇᴀʀᴄʜ 𝖸ᴏᴜʀ 𝖮ᴡɴ 𝖥ɪʟᴇ, 𝖣ᴏɴ'ᴛ 𝖢ʟɪᴄᴋ 𝖮ᴛʜᴇʀ𝗌 𝖱ᴇ𝗌ᴜʟᴛ𝗌 😬", show_alert=True)
    if movie_  == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.message_id)
    if not movies:
        return await query.answer(f"⚠️ Hey, {query.from_user.first_name}! You Are Clicking On An Old Button Which Is Expired ⚠️", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('🔎 Checking for Movie in My database... 🔎')
    files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        k = await query.message.edit(f'⚠️ 𝖧ᴇʏ, {query.from_user.first_name} ! 𝖳ʜɪ𝗌 𝖬ᴏᴠɪᴇ/𝖲ᴇʀɪᴇ𝗌 𝖭ᴏᴛ Aᴅᴅᴇᴅ Iɴ @Filmokamella Dᴀᴛᴀʙᴀ𝗌ᴇ ⚠️')
        await asyncio.sleep(10)
        await k.delete()
    

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            grpid  = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == "creator") or (str(userid) in ADMINS):    
            await del_all(query.message, grp_id, title)
        else:
            await query.answer(f"🤒 Hey, {query.from_user.first_name}! You Need To Be Group Owner Or An Auth User To Do That! 🤒",show_alert=True)

    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == "creator") or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer(f"⚠️ Hey, {query.from_user.first_name}! That's Not For You!! ⚠️",show_alert=True)


    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]
        
        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode="md"
        )
        return

    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text('Some Error Occurred!!', parse_mode="md")
        return
   
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text(
                f"Some Error Occurred!!",
                parse_mode="md"
            )
        return
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully Deleted Connection"
            )
        else:
            await query.message.edit_text(
                f"Some Error Occurred!!",
                parse_mode="md"
            )
        return
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There Are No Active Connections!! Connect To Some Groups First.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert,show_alert=True)

    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer(f'Hey, {query.from_user.first_name}! No Such File Exist. Send Request Again')
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
            
        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            elif P_TTI_SHOW_OFF:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                    )
                await query.answer(f'Hey {query.from_user.first_name} Check PM, I have sent files in pm',show_alert = True)
        except UserIsBlocked:
            await query.answer(f'Hey {query.from_user.first_name} Unblock the bot mahn !',show_alert = True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer(f"Hey, {query.from_user.first_name}! I Like Your Smartness, But Don't Be Oversmart 😒",show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer(f'Hello, {query.from_user.first_name}! No Such File Exist. Send Request Again')
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
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            reply_markup=InlineKeyboardMarkup(buttons)
            )

    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
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
        await query.message.edit_text(
            text=Script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "help":
        buttons =  [[
            InlineKeyboardButton('ʀᴇᴀᴅ ᴛᴜᴛᴏʀɪᴀʟ', url='https://telegra.ph/How-To-Use-iFilms-Movie-Bot-01-15')
            ],[
            InlineKeyboardButton('ᴀᴅᴍɪɴ', callback_data='admin'),
            InlineKeyboardButton('ᴄᴏɴɴᴇᴄᴛ', callback_data='coct'),
            InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇs', callback_data='ifsupd')
            ],[
            InlineKeyboardButton('ᴀᴜᴛᴏ', callback_data='autofilter'),
            InlineKeyboardButton('ғɪʟᴛᴇʀs', callback_data='manuelfilter'),
            InlineKeyboardButton('ʙᴜᴛᴛᴏɴs', callback_data='button')
            ],[
            InlineKeyboardButton('ᴘᴀsᴛᴇ', callback_data='paste'),
            InlineKeyboardButton('ᴘᴜʀɢᴇ', callback_data='purge'),
            InlineKeyboardButton('ᴘɪɴ', callback_data='pin')
            ],[
            InlineKeyboardButton('sᴇᴀʀᴄʜ', callback_data='extra'),
            InlineKeyboardButton('ʀᴇsᴛʀɪᴄ', callback_data='restric'),
            InlineKeyboardButton('ᴜsᴇʀs', callback_data='usersinfo')
            ],[
            InlineKeyboardButton('ᴘ-ɢᴇɴ', callback_data='genpassword'),
            InlineKeyboardButton('ᴛ-ɢʀᴀᴘʜ', callback_data='tgraph'),
            InlineKeyboardButton('sᴛʀɪɴɢ', callback_data='genstring')
            ],[
            InlineKeyboardButton('ᴜʀʟs', callback_data='shortner'),
            InlineKeyboardButton('sᴘᴇᴇᴄʜ', callback_data='tts'),
            InlineKeyboardButton('ɢ-ᴛʀᴀɴs', callback_data='gtrans')
            ],[
            InlineKeyboardButton('ᴍᴜsɪᴄ', callback_data='pmusic'),
            InlineKeyboardButton('ʏᴏᴜᴛᴜʙᴇ', callback_data='music'),
            InlineKeyboardButton('ɢᴀᴍᴇs', callback_data='games')
            ],[
            InlineKeyboardButton('ɢᴜɪᴅᴇ', callback_data='guide'),
            InlineKeyboardButton('zᴏᴍʙɪᴇs', callback_data='zombies'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about')
            ],[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='start'),
            InlineKeyboardButton('sᴛᴀᴛᴜs', callback_data='stats'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.HELP_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "about":
        buttons= [[
            InlineKeyboardButton('Sᴛᴀᴛᴜs', callback_data='stats'),
            InlineKeyboardButton('Sᴏᴜʀᴄᴇ', callback_data='source')
            ],[
            InlineKeyboardButton('Rᴇᴘᴏʀᴛ Bᴜɢs & Fᴇᴇᴅʙᴀᴄᴋ', url=f'https://t.me/{SUPPORT}')
            ],[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='start'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.ABOUT_TXT.format(temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='about'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.SOURCE_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "genstring":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.STRING_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "ifsupd":
        buttons = [[
            InlineKeyboardButton('📢 Jᴏɪɴ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ!', url=f'https://t.me/{UPDATES}')
            ],[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')   
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.IFSUPD_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')   
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "guide":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')   
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.GUIDE_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "usersinfo":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')   
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.USERSINFO_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "games":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')   
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.GAMES_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "paste":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.PASTE_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "pmusic":
        buttons = [[
            InlineKeyboardButton('🤖 Sᴛᴀʀᴛ Tʜᴇ Bᴏᴛ 🤖', url='https://t.me/IFS_MUSIC_BOT')
            ],[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')   
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.PMUSIC_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "tgraph":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.TGRAPH_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "gtrans":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.GTRANS_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "zombies":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.ZOMBIES_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "purge":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.PURGE_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "restric":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.RESTRIC_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "shortner":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.URL_SHORTNER_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "tts":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.TTS_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "pin":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.PIN_MESSAGE_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "music":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.MUSIC_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "genpassword":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('Cʟᴏsᴇ ✗', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=Script.PASSWORD_GEN_TXT,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='about'),
            InlineKeyboardButton('Rᴇғᴇʀsʜ ⧖', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=Script.STATUS_TXT.format(total, users, chats, monsize, free),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching iFilms DataBase")
        buttons = [[
            InlineKeyboardButton('« Bᴀᴄᴋ', callback_data='about'),
            InlineKeyboardButton('Rᴇғᴇʀsʜ ⧖', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=Script.STATUS_TXT.format(total, users, chats, monsize, free),
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            parse_mode='html'
      )
    elif query.data == "delit":
        chat_type = query.message.chat.type
        if chat_type == 'private':
            await query.message.delete()
            await query.answer('Deleted!😎')
        elif query.from_user.id == query.message.reply_to_message.from_user.id:
            msg = query.message.reply_to_message
            await msg.delete()
            await query.message.delete()
            await query.answer('Deleted!😎')
        else:
            await query.answer('Not yours!', show_alert = True)
          

async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if SPELL_CHECK_REPLY:
                    await client.send_message(LOG_CHANNEL, Script.NO_RESULTS_TXT.format(message.from_user.id, message.from_user.mention, message.text))
                    return await advantage_spell_chok(msg)
               
                else:
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message # msg will be callback query
        search, files, offset, total_results = spoll
    if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f'files#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if offset != "":
        key = f"{message.chat.id}-{message.message_id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [   InlineKeyboardButton(text=f"🗓 1/{round(int(total_results)/10)}",callback_data="pages"),
                InlineKeyboardButton(text="🗑",callback_data="delit"), 
                InlineKeyboardButton(text="Nᴇxᴛ »",callback_data=f"next_{req}_{key}_{offset}")
            ],
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1 🗓",callback_data="pages")]
        )

    reply_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id
    imdb = await get_poster(search, file=(files[0]).file_name) if IMDB else None
    if imdb:
        cap = IMDB_TEMPLATE.format(
            query = search,
            title = imdb['title'],
            votes = imdb['votes'],
            aka = imdb["aka"],
            seasons = imdb["seasons"],
            box_office = imdb['box_office'],
            localized_title = imdb['localized_title'],
            kind = imdb['kind'],
            imdb_id = imdb["imdb_id"],
            cast = imdb["cast"],
            runtime = imdb["runtime"],
            countries = imdb["countries"],
            certificates = imdb["certificates"],
            languages = imdb["languages"],
            director = imdb["director"],
            writer = imdb["writer"],
            producer = imdb["producer"],
            composer = imdb["composer"],
            cinematographer = imdb["cinematographer"],
            music_team = imdb["music_team"],
            distributors = imdb["distributors"],
            release_date = imdb['release_date'],
            year = imdb['year'],
            genres = imdb['genres'],
            poster = imdb['poster'],
            plot = imdb['plot'],
            rating = imdb['rating'],
            url = imdb['url'],
            **locals()
        )
    else:
        cap = f"Here Is What I Found For Your Query {search}"
    if imdb and imdb.get('poster'):
        try:
            delmsg = await message.reply_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(5400)
            await delmsg.delete()
            await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            delmsg = await message.reply_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(5400)
            await delmsg.delete()
            await message.delete()
        except Exception as e:
            logger.exception(e)
            delmsg = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(5400)
            await delmsg.delete()
            await message.delete()
    else:
        delmsg = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(5400)
        await delmsg.delete()
        await message.delete()
    if spoll:
        await msg.message.delete()
        

async def advantage_spell_chok(msg):
    query = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)", "", msg.text, flags=re.IGNORECASE) # plis contribute some common words 
    query = query.strip() + " movie"
    search = msg.text
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        if message.chat.id in filters.chat(chats=-1001114885212):
           button = InlineKeyboardMarkup(
           [[
             InlineKeyboardButton("ɢᴏᴏɢʟᴇ ꜱᴇᴀʀᴄʜ", url=f"https://www.google.com/search?q={search}"),
             InlineKeyboardButton("ɪᴍᴅʙ ꜱᴇᴀʀᴄʜ", url=f"https://www.imdb.com/find?q={search}")
           ]])
           k = await msg.reply_photo(photo="https://telegra.ph/file/eeaad7f955a7cbf7d60c0.jpg", caption="<b>ʜᴇʏ, ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ᴍᴏᴠɪᴇ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ 😔</b>\n\n<b>ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>", reply_markup=button)
           await asyncio.sleep(20)
           await k.delete()
           return
        except:
            pass
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE) # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)', '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*", re.IGNORECASE) # match something like Watch Niram | Amazon Prime 
        for mv in g_s:
            match  = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed)) # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True) # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist)) # removing duplicates
    if movielist:
        if message.chat.id in filters.chat(chats=-1001114885212):
           button = InlineKeyboardMarkup(
           [[
             InlineKeyboardButton("ɢᴏᴏɢʟᴇ ꜱᴇᴀʀᴄʜ", url=f"https://www.google.com/search?q={search}"),
             InlineKeyboardButton("ɪᴍᴅʙ ꜱᴇᴀʀᴄʜ", url=f"https://www.imdb.com/find?q={search}")
           ]])
           k = await msg.reply_photo(photo="https://telegra.ph/file/eeaad7f955a7cbf7d60c0.jpg", caption="<b>ʜᴇʏ, ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ᴍᴏᴠɪᴇ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ 😔</b>\n\n<b>ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>", reply_markup=button)
           await asyncio.sleep(20)
           await k.delete()
           return
        except:
            pass

    if not movielist:
        if message.chat.id in filters.chat(chats=-1001114885212):
           button = InlineKeyboardMarkup(
           [[
             InlineKeyboardButton("ɢᴏᴏɢʟᴇ ꜱᴇᴀʀᴄʜ", url=f"https://www.google.com/search?q={search}"),
             InlineKeyboardButton("ɪᴍᴅʙ ꜱᴇᴀʀᴄʜ", url=f"https://www.imdb.com/find?q={search}")
           ]])
           k = await msg.reply_photo(photo="https://telegra.ph/file/eeaad7f955a7cbf7d60c0.jpg", caption="<b>ʜᴇʏ, ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴛʜᴇ ᴍᴏᴠɪᴇ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ 😔</b>\n\n<b>ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>", reply_markup=button)
           await asyncio.sleep(20)
           await k.delete()
           return
        except:
            pass

async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.message_id if message.reply_to_message else message.message_id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True, reply_to_message_id=reply_id)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id, 
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id = reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id = reply_id
                        )
                    else:
                        button = eval(btn) 
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id = reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
