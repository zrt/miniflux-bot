from telegram.ext import Updater, CommandHandler
import config
import requests
import logging
import re
import json, time
import os
import miniflux_client
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

updater = Updater(config.TOKEN)
bot = updater.bot
jq = updater.job_queue


try:
    with open('latest.txt') as f:
        latest = int(f.read().strip())
    print('load latest %d'%latest)
except:
    print('latest = -1')
    latest = -1

htmltag = re.compile(r'</?\w+[^>]*>')
def escapehtml(s):
    return htmltag.sub('',s)

def get_info(entry):
    ret = ''
    ret += "<b>%s</b>\n"%entry['title']
    if len(entry['author']) > 0:
        ret += '#%s\n'%entry['author']
    ret += entry['url']+'\n'
    ret += '%s, #%d\n'%(entry['published_at'],entry['id'])
    s = escapehtml(entry['content'])
    s = s.replace('\r', '')
    while '\n\n' in s:
        s = s.replace('\n\n','\n')
    if len(s) < config.maxlen:
        ret += s
    else:
        ret += s[:config.maxlen] +'...'
    return ret

def send_entry(bot, entry):
    text = get_info(entry)
    bot.send_message(
        chat_id=config.channel_id, 
        text=text,
        parse_mode = 'html'
    )

def check(bot):
    global latest
    entries = miniflux_client.get_entries(latest)
    for x in entries:
        send_entry(bot, x)
        latest = max(latest, x['id'])

def check_wrapper(bot, context):
    check(bot)

check_job = jq.run_repeating(check_wrapper, interval = config.check_interval_in_mins * 60, first = 5)

updater.start_polling()
updater.idle()

print('saving...')
with open('latest.txt', 'w') as f:
    f.write('%d'%latest)
print('saved')
