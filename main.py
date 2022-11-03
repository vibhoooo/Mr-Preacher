import discord
import os
import requests  # for making http calls
import json  # converting data in json
import random
from replit import db
from keep_alive import keep_alive  # importing the web server


# now our basic bot is ready and now we can add other features to it
# this will give random inspirational quotes from the selected api
# here I have used https://zenquotes.io/
def get_quote():
    # storing response
    response = requests.get('https://zenquotes.io/api/random')
    # converting response into json
    json_data = json.loads(response.text)
    # taking out quote from json
    quote = json_data[0]['q'] + ' ->' + json_data[0]['a']
    return quote


# now we will make our bot respond when ever our user enters any sad message
# what I want to say is that whenever our bot will notice any sad word in our message it wil start preaching
sad_words = [
    'sad', 'depressed', 'unhappy', 'miserable', 'anxiety', 'depressing'
]

starter_encouragements = [
    'Cheer up!', 'Hang in there...', 'You are an incredible person'
]

# responding only if True and not always
if 'responding' not in db.keys():
    db['responding'] = True


# here now we will use replits built in database to store user submitted messages in the database
def update_encouragemets(encouraging_message):
    if 'encouragements' in db.keys():
        encouragements = db['encouragements']
        encouragements.append(encouraging_message)
        db['encouragements'] = encouragements
    else:
        db['encouragements'] = [encouraging_message]


def delete_encouragement(index):
    encouragements = db['encouragements']
    if len(encouragements) > index:
        del encouragements[index]
        db['encouragements'] = encouragements


# instance of the client
intent = discord.Intents.default()
intent.members = True
intent.message_content = True

client = discord.Client(intents=intent)


# using instance of client to register an event
@client.event
# this event is called when bot is ready to being used
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# using instance of client to register an event
@client.event
# this event triggers each time a message is received but that message should not from the bot itself
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$h'):
        await message.channel.send('Hola!! here comes ur preacher')
    msg = message.content
    if message.content.startswith('$i'):
        quote = get_quote()
        await message.channel.send(quote)
    # responding only if user enters True
    if db['responding']:
        options = starter_encouragements
        if 'encouragements' in db.keys():
            options = options + db['encouragements'].value
        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(options))
    if msg.startswith('$new'):
        encouraging_message = msg.split('$new ', 1)[1]
        update_encouragemets(encouraging_message)
        await message.channel.send('New encouaraging message added...')
    if msg.startswith('$del'):
        encouragements = []
        if 'encouragements' in db.keys():
            index = int(msg.split('$del', 1)[1])
            delete_encouragement(index)
            encouragements = db['encouragements']
        await message.channel.send(encouragements)
    # listing feature
    if msg.startswith('$list'):
        encouragements = []
        if 'encouragements' in db.keys():
            encouragements = db['encouragements']
        await message.channel.send(encouragements)
    # asking permission from  the user whether the bot should respond to sad messages or not
    # if user enters True then the bot will reply to sad messages
    if msg.startswith('$responding'):
        value = msg.split('$responding ', 1)[1]
        if value.lower() == 'true':
            db['responding'] = True
            await message.channel.send('Responding is on...')
        else:
            db['responding'] = False
            await message.channel.send('Responding is off...')


# calling the function to run the web server
keep_alive()
# command to run a bot
client.run(os.getenv('TOKEN'))
