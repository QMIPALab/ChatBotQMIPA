import discord
import os
import logging
import re

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer

DISCORD_BOT_KEY = os.environ.get('token')

logging.basicConfig(level=logging.INFO)

# Create a new ChatBot instance
bot = ChatBot(
    'DiscorderBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database='./db.psql',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'statement_comparison_function': 'chatterbot.comparisons.levenshtein_distance',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.60
        },
        {
            'import_path': 'chatterbot.logic.MathematicalEvaluation'
        },
        {
            'import_path': 'chatterbot.logic.WikipediaResponseAdapter'
        }
    ],
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace'
    ],
    filters=[
        'chatterbot.filters.RepetitiveResponseFilter'
    ],
)
trainer = ChatterBotCorpusTrainer(bot)

trainer.train("./Gabungan")

def train(content):
    trainer = ListTrainer(bot)
    trainer.train(content)
    thanks = 'thank you for training me'
    return thanks

def get_response(content):
        return bot.get_response(content)


async def check_for_trigger_match(query, trigger_list):
    for trigger in trigger_list:
        if query.startswith(trigger):
            return trigger


async def remove_bot_reference(query, bot_trigger):
    src_str = re.compile(bot_trigger, re.IGNORECASE)
    query = src_str.sub('', query)
    return query


# Create Discord client - wraps our bot and reads all input but only send a response if the bot is being spoken to
client = discord.Client()

# set global discordBot references to be accessed once on_ready is fired
botName = ''
botNameCleaned = ''
botId = 0

triggers = []
triggersLower = []


@client.event
async def on_ready():
    try:
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

        global botName
        botName = client.user.name
        global botNameCleaned
        botNameCleaned = ''.join(e for e in botName if e.isalnum())
        global botId
        botId = client.user.id

        # define trigger terms for our bot
        global triggers
        triggers = {botName, botNameCleaned, '<@!' + str(botId) + '>', 'hey <@!' + str(botId) + '>', 'hey ' + botName,
                    'hey ' + botNameCleaned, 'hi ' + botName, 'hi ' + botNameCleaned, 'oi ' + botName,
                    'oi ' + botNameCleaned}
        global triggersLower
        triggersLower = [x.lower() for x in triggers]
        
        global trainingtrigger
        trainingtriggers ={'train ' + botName,'belajar ' + botName,'train '+ botNameCleaned , 'belajar ' + botNameCleaned}
        
        global trainingtriggersLower
        trainingtriggersLower = [x.lower() for x in trainingtriggers]

        global endtrainingtrigger
        trainingtriggers ={'end training ' + botName,'belajar selesai ' + botName,'end training '+ botNameCleaned , 'belajar selesai' + botNameCleaned}
        
        global endtrainingtriggersLower
        trainingtriggersLower = [x.lower() for x in endtrainingtriggers]

    except Exception as e:
        print(e.args)


@client.event
async def on_message(message):
    try:
        user = message.author

        # Checking that the message is not from our bot - we don't want it replying to itself into infinity!
        if not user.bot:
            replying = False
            training = False

            query_string = message.content
            query_string_to_lower = query_string.lower()

            # check if Bot has been summoned and set 'replying' to true
            matching_trigger = await check_for_trigger_match(query_string_to_lower, triggersLower)
            matching_starttrainingtrigger = await check_for_trigger_match(query_string_to_lower, trainingtriggersLower)
            matching_trainingtrigger = await check_for_trigger_match(query_string_to_lower, '!')
            matching_endtrainingtrigger = await check_for_trigger_match(query_string_to_lower, endtrainingtriggersLower)

            if matching_trigger:
                replying = True
                query_string = await remove_bot_reference(query_string, matching_trigger)

            # clean string before persisting to DB
            query_string = query_string.lstrip(" ,.?;][}{%@$^&*")
            response = str(get_response(query_string))

            if matching_starttrainingtrigger
                starttraining = True
            
            if matching_trainingtrigger:
                trainingdata = []
                trainingdata.append(query_string)
                return trainingdata

            if matching_endtrainingtrigger:
                train(query_string)
                trainingdata = []
                trainingend = True

            # Here we only reply if replying is set to true
            if starttraining:
                starttraining = 'To train me use ! in front of your text, make it a conversation end end the training by typing end training/belajar selesai and my name'
                embed=discord.Embed(title="QbotBeta", description = response, color = (0xF48D1))
                await message.channel.send(embed=embed)
            
            if replying:
                embed=discord.Embed(title="QbotBeta", description = response, color = (0xF48D1))
                await message.channel.send(embed=embed)

            if trainingend:
                trainingendresponse = 'Thank you for training me'
                embed=discord.Embed(title="QbotBeta", description = trainingendresponse, color = (0xF48D1))
                await message.channel.send(embed=embed)
                return trainingdata

    except Exception as err:
        print(err.args)


try:
    client.run(DISCORD_BOT_KEY)
except IOError as e:
    print(e.args)
else:
    print('Discord connection closed. Closing Process.')
