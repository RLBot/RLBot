from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters


# In order to run this successfully:
# 1. Run 'pip install py4j'  (one time setup)
# 2. Modify runner.py to use this agent, e.g. "import JavaAgent as agent2"
# 3. Choose a port number, and put it both in this class and in AgentEntryPoint.java
#    - Avoid 25333 because that's the default, and other bots may be using it!
#    - See the myPort variable below, which I've set to -1 so that you're forced to see this.
# 4. Run the AgentEntryPoint class, and leave it running
# 5. Run runner.py

'''
Hi! You can use this code as a template to create your own bot.  Also if you don't mind writing a blurb
about your bot's strategy you can put it as a comment here. I'd appreciate it, especially if I can help
debug any runtime issues that occur with your bot.
'''

# Optional Information. Fill out only if you wish.

# Your real name:
# Contact Email:
# Can this bot's code be shared publicly (Default: No):
# Can non-tournment gameplay of this bot be displayed publicly (Default: No):

myPort = -1  # -1 fails on purpose, see instructions above to change it!
if myPort < 0:
	# Feel free to remove this once you've chosen a port!
	raise Exception('The person programming this bot (you?) needs to choose a port number! See instructions in this file')


# Scenario: you finished your bot and submitted it to a tournament. Your opponent hard-coded the same
# as you, and the match can't start because of the conflict. Because of this line, you can ask the
# organizer make a file called "port.txt" in the same directory as your .jar, and put some other number in it.
# This matches code in AgentEntryPoint.java
try:
	with open("port.txt", "r") as portFile:
		myPort = int(portFile.readline())
except ValueError:
	print("Failed to parse port file! Will proceed with hard-coded port number.")
except:
	pass

print("Connecting to Java Gateway on port " + str(myPort))
gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True, port=myPort))
javaAgent = gateway.entry_point.getAgent()


# This is the name that will be displayed on screen in the real time display!
BOT_NAME = "JavaAgent"

class agent:

	def __init__(self, team):
		self.team = team # use self.team to determine what team you are. I will set to "blue" or "orange"

	def get_output_vector(self, input):
		# Call the java process to get the output
		listOutput = javaAgent.getOutputVector([list(input[0]), list(input[1])], self.team)
		# Convert to a regular python list
		return list(listOutput)

	