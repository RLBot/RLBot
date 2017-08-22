from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters


# In order to run this successfully:
# 1. Run 'pip install py4j'  (one time setup)
# 2. Modify runner.py to use this agent, e.g. "agent2 = JavaAgent.agent("orange")"
# 3. Run the AgentEntryPoint class, and leave it running
# 4. Run runner.py

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

class agent:

	def __init__(self, team):
		self.team = team # use self.team to determine what team you are. I will set to "blue" or "orange"
		self.gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True))
		self.agent = self.gateway.entry_point.getAgent()

	def get_bot_name(self):
		# This is the name that will be displayed on screen in the real time display!
		return "JavaAgent"

	def get_output_vector(self, input):
		return self.agent.getOutputVector(input, self.team)

	