from Cerebro import Neuronio
import random, telepot, telepot.helper, time, datetime, sys, re, os, subprocess
sudo = 438131290
maintenance = True
Chatsuporte = 438131290
TOKEN = "468247740:AAGQM8khZ-VdF3_wagCrnb3YjS_6cQ0HTbk"
api = telepot.Bot(TOKEN)
bot = api.getMe()
bot_name = bot['first_name']
bot_username = '@{}'.format(bot['username'])
bot_id = str(bot['id'])
AIAPI = Neuronio.Kernel()
AIAPI.setBotPredicate('name',  bot_name)
AIAPI.setBotPredicate('sexo',  "mulher")
AIAPI.setBotPredicate('sexo_tipo',  "Fema")
AIAPI.setBotPredicate('sexoposto',  "homem")
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardRemove, ForceReply, InlineQueryResultPhoto
from telepot.delegate import (
    per_chat_id, per_from_id, per_callback_query_origin, create_open, pave_event_space)
from telepot.exception import BotWasBlockedError
from utils.tools import gsub, conversor, uptime, AI, bash
from utils.utils import gameMat, Viewer, NSFW, URL_JSON, SendType
from utils.keyboards import *
from lang.lang import lang
from lang.Subs import *
from plugins.simple import simple
from plugins.Init import help
from plugins.Mediatype import midia
from plugins.control_sudo import control_plugin
from plugins.IA import IA, Chat, CleanReacion
from bot import main
from CallbackQuery import Callback
