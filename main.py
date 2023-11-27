import discord
import random
from discord.ext import commands
#do this when testing the hosting or whatever
#from constant_pinging import keep_alive

#maybe add this to an env so it's private
token = "MTEyNDU3ODg4MTg2NTc3NzI1Mg.GPTbl6.1Cv4TktMWmcml-ec0U5bJyDsOVJSWoNp2D6Ofc"
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
#client = discord.Client(intents=intents)
"""Defining bot for commands and such?  maybe need to rewrite things above"""
bot = commands.Bot(command_prefix="!", intents=intents)

#tracking queues
global queueList
queueList = []

global playerInfo
playerInfo = []

global queueSize
queueSize = 0

global MAX
MAX = 1  #change to 10 when pushed

global queueLock
queueLock = False

global teamA
teamA = []
global teamB
teamB = []

global numberedPlayers
numberedPlayers = ""

@bot.event
async def on_ready():
  print("Bot is ready")
  #discord streaming status
  await bot.change_presence(activity=discord.Streaming(
    name='!help Crimson Queue', url='https://www.twitch.tv/illusionmonkey'))


#Greeting
@bot.event
async def on_message(message):
  #global variables
  global queueList, queueSize, MAX, queueLock

  #greeting
  if message.author == bot.user:
    return
  if message.content.startswith("What's up CHBot"):
    await message.channel.send("What's up pussy")
    #dms user
    await message.author.send("I found your bitchass")  #how to dm users
    user1 = message.author
    print(message.author)
    await user1.send(
      "This is a test"
    )  #use user class object.send to send a method to a specific user, you hold the user class object in queueList[]

  #listing bot commands
  if message.content.startswith("!help") or message.content.startswith(
      "!commands"):
    await message.channel.send(
      "__Commands:__\n-!q - This command is used to join the ongoing queue or start your own queue for others to join.\n-!leave  - Allows you to leave the current queue.\n-!status  - Shows you all the current players that are in the queue as well as their roles."
    )
        
  """!queue command, currently using placeholder role of jungle"""
  #can use a switch statement and "message.content.contains" for the individual roles and assign a string to it
  if message.content.startswith("!q"):
    inQueue = False
    #iterating array to check if in queue
    for i in queueList:
      #if user is already in queue
      if (i[0] == "<@" + str(message.author.id) + ">"):
        await message.channel.send("**User is already in queue**")
        inQueue = True
    #if user not in queue and not max size and queue is not locked
    if (inQueue == False and queueSize < MAX and queueLock == False):
      #incrementing queueSize
      queueSize = queueSize + 1
      #populating queueList by Username, Role, Current LP, and user object
      playerInfo = [
        "<@" + str(message.author.id) + ">", "Jungle", "100", message.author
      ]
      queueList.append(playerInfo)
      await message.channel.send("<@" + str(message.author.id) + ">" +
                                 " **has entered the queue\n" +
                                 str(queueSize) +
                                 " players are in the queue**")
      #debug for queue
      print(str(playerInfo) + " has entered queue\n")
      print((type(playerInfo[3])))

    #if queue hits max, calls queue_pop and locks queue
    if (queueSize == MAX):
      queueLock = True
      await queue_pop(message)
      
  """!leave command"""
  if message.content.startswith("!leave"):
    inQueue = False
    if (queueLock == True):
      print("Queue lock is on currently, player cannot leave queue\n")  #debug
    #iterating array to check if in queue
    for i in queueList:
      #if user is already in queue
      if (i[0] == "<@" + str(message.author.id) + ">"):
        inQueue = True
    #if user not in queue
    if (inQueue == True and queueLock == False):
      #temp list that will become new queueList with removed user
      queueCopy = []
      #iterating through queueList
      for i in queueList:
        #if user, don't add to queueCopy
        if not (i[0] == "<@" + str(message.author.id) + ">"):
          queueCopy.append(i)
      #overriding queueList with new list
      queueList = queueCopy
      #decrementing queueSize
      queueSize = queueSize - 1
      await message.channel.send("**" + str(queueSize) +
                                 " players are in the queue**")

      #debug
      if (len(queueList) != 0):
        print("Current queueList: \n")
        tempStr = ""
        for i in queueList:
          for j in i:
            tempStr = tempStr + str(j) + " "
          tempStr = tempStr + "\n"
        await message.channel.send(tempStr)
        print(tempStr)
        
  """!status command"""
  if message.content.startswith("!status"):
    #if queue is locked
    if (queueLock == True):
      await message.channel.send("**Queue is closed, game active**")
    #if queueList isn't empty
    elif (len(queueList) != 0):
      strStatus = "__Queue Status__\n**Players currently in queue:**\n"
      #iterate through queueList and display in message
      for i in queueList:
        for j in range(3):
          strStatus = strStatus + str(i[j]) + " "
        strStatus = strStatus + "LP\n"
      await message.channel.send(strStatus)
    else:
      await message.channel.send("**There are no players currently in queue**")


"""Print players function, returns string of players numbered"""
@bot.event
async def printPlayers():
  global queueList, numberedPlayers  #might not be needed

  strStatus = ""
  counter = 1  #counter for player number
  for i in queueList:
    strStatus = strStatus + "- [" + str(counter) + "] "   
    for j in range(3):
      strStatus = strStatus + str(i[j]) + " "
    strStatus = strStatus + "LP\n"
    counter += 1  #increments counter

  numberedPlayers = strStatus
  


"""Queue pop function"""
@bot.event
async def queue_pop(message):
  #global variables
  global queueList, queueSize, MAX, teamA, teamB, numberedPlayers

  
  strPlayers = ""
  #notify players of queuePop
  await message.channel.send("Reached " + str(MAX) + " players!")
  #iterate through queueList and @mention players
  for i in queueList:
    strPlayers = strPlayers + str(i[0]) + ", "
  strPlayers = strPlayers[0:len(strPlayers) - 2]

  #sorts queueList high to low based on LP          #now have user object at end, need to make sure the sorting still works
  sorted(queueList, key=lambda l: l[1], reverse=True)
  """Captains Voting"""
  #captains are randomly picked between the 3 highest LP
  rand1 = random.randint(0, 2)
  rand2 = -1
  """while (rand2 != -1 and rand1 != rand2):
    rand2 = random.randint(0, 2)
  #logic for captains
  if (rand1 == 0):
    teamA.append(queueList[0])
  elif (rand1 == 1):
    teamA.append(queueList[1])
  else:
    teamA.append(queueList[2])
  if (rand2 == 0):
    teamB.append(queueList[0])
  elif (rand2 == 1):
    teamB.append(queueList[1])
  else:
    teamB.append(queueList[2])
  """
  teamA.append(queueList[0])
  #stores user objects of both captains for ease of access
  captainA = teamA[0][3]
  #captainB = teamB[0][3]

  #messaging captains for picks
  await printPlayers()
  await captainA.send("**Please select your first player:**\n" + numberedPlayers)

  #captainA pick (make this a function, and have it not include the other captain in the list) also remove the chosen players from queueList as you go

  if (message.author == captainA):
    if (message.content.startswith("1")):
      teamA.append(queueList[0])
    elif (message.content.startswith("2")):
      teamA.append(queueList[1])
    elif (message.content.startswith("3")):
      teamA.append(queueList[1])
    elif (message.content.startswith("4")):
      teamA.append(queueList[1])
    elif (message.content.startswith("5")):
      teamA.append(queueList[1])
    elif (message.content.startswith("6")):
      teamA.append(queueList[1])
    elif (message.content.startswith("7")):
      teamA.append(queueList[1])
    elif (message.content.startswith("8")):
      teamA.append(queueList[1])
    elif (message.content.startswith("9")):
      teamA.append(queueList[1])
  """#iterates through both and appends to string to send as message
  teams = ""
  for i in range(MAX/2):    #change to MAX/2 when pushed
    temp = teamA[i]
    teams = teams + temp[0] + "\t\t\t\t\t\t\t\t\t\t"
    temp = teamB[i]
    teams = teams + temp[0] + "\n"
  #printing the teams
  await message.channel.send("**Team A:                    Team B:**\n" + teams)"""
  """ This is for voting, just use random or balanced for now
  #voting hardcoded formatting
  await message.channel.send(strPlayers + "\nVoting will commence now")
  await message.channel.send("**Vote for random teams:  Vote for captains:  Vote for balanced teams:**\n!r\t\t\t\t\t\t\t\t\t\t\t   !c\t\t\t\t\t\t\t\t  !b")
  
  #eventually you will need to have this make sure that the players voting are actually part of the teams | also make sure they can't vote twice :shrug:
  #counters for votes
  rCount = 0
  cCount = 0
  bCount = 0
  #while counter is less than half the total players, keep voting open
  #change to MAX/2 when pushed
  while (rCount < MAX/2 or cCount < MAX/2 or bCount < MAX/2):
    #if vote random add to counter
    if (message.content.startswith("!r")):
      rCount += 1
    if (message.content.startswith("!c")):
      cCount += 1
    if (message.content.startswith("!b")):
      bCount += 1
  #random
  if (rCount >= MAX/2):
    await message.channel.send("Random was chosen")
    #debug
    print("Random was chosen")
    """


bot.run(token)
#keep_alive()

#client.run(os.getenv("token")) old way to get through env
#client.run(token)
