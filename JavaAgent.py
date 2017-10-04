from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters
import cStructure


# In order to run this successfully:
# 1. Run 'pip install py4j'  (one time setup)
# 2. Modify rlbot.cfg so that one of the agents is JavaAgent, e.g. "p2Agent = JavaAgent"
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

# This is the name that will be displayed on screen in the real time display!
BOT_NAME = "JavaAgent"

class agent:

	def __init__(self, team):
		self.team = team # use self.team to determine what team you are. I will set to "blue" or "orange"
		self.myPort = -1  # -1 fails on purpose, see instructions above to change it!
		if self.myPort < 0:
			# Feel free to remove this once you've chosen a port!
			raise Exception('The person programming this bot (you?) needs to choose a port number! See instructions in this file')

		# Scenario: you finished your bot and submitted it to a tournament. Your opponent hard-coded the same
		# as you, and the match can't start because of the conflict. Because of this line, you can ask the
		# organizer make a file called "port.txt" in the same directory as your .jar, and put some other number in it.
		# This matches code in AgentEntryPoint.java
		try:
			with open("port.txt", "r") as portFile:
				self.myPort = int(portFile.readline())
		except ValueError:
			print("Failed to parse port file! Will proceed with hard-coded port number.")
		except:
			pass

		try:
			self.init_py4j_stuff()
		except:
			print("Exception when trying to connect to java! Make sure the java program is running!")
			pass


	def init_py4j_stuff(self):
		print("Connecting to Java Gateway on port " + str(self.myPort))
		self.gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True, port=self.myPort))
		self.javaAgent = self.gateway.entry_point.getAgent()
		print("Connection to Java successful!")


	def get_output_vector(self, sharedValue):
		try:
			input_json = cStructure.gameTickPacketToJson(sharedValue.GameTickPacket)
			# Call the java process to get the output
			listOutput = self.javaAgent.getOutputVector(input_json, self.team)
			# Convert to a regular python list
			return list(listOutput)
		except Exception as e:
			print("Exception when calling java: " + str(e))
			print("Will recreate gateway...")
			self.gateway.shutdown_callback_server()
			try:
				self.init_py4j_stuff()
			except:
				print("Reinitialization failed")
				pass

			return [16383, 16383, 0, 0, 0, 0, 0] # No motion
