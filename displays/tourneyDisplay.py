import PIL.Image
import PIL.ImageTk

'''
This file requires Pillow!  Do a "pip install pillow" to use this display
'''

from tkinter import *

class real_time_display:
	
	# Variables
	root = Tk()
	
	background = PIL.ImageTk.PhotoImage(PIL.Image.open("./displays/images/background.png"))
	stickzone = PIL.ImageTk.PhotoImage(PIL.Image.open("./displays/images/stickzone.png"))
	marker = PIL.ImageTk.PhotoImage(PIL.Image.open("./displays/images/marker.png"))
	
	canvas = Canvas(root, height=332, width=248, borderwidth=0)
	
	p1marker = 0
	p2marker = 0
	p1decel = 0
	p1acel = 0
	p2decel = 0
	p2acel = 0
	p1a = 0
	p1b = 0
	p1x = 0
	p2a = 0
	p2b = 0
	p2x = 0
	p1score = 0
	p1goals = 0
	p1owngoals = 0
	p1shots = 0
	p1saves = 0
	p1demos = 0
	p2score = 0
	p2goals = 0
	p2owngoals = 0
	p2shots = 0
	p2saves = 0
	p2demos = 0
	p1scoreboardscore = 0
	p2scoreboardscore = 0
	timeremaining = 0
	ball = 0
	blue = 0
	orng = 0
	
	PLAYER_PIXEL_SIZE = 4
	FIELD_WIDTH = 242
	FIELD_HEIGHT = 162
	UU_FIELD_WIDTH = 11880
	UU_FIELD_HEIGHT = 8160
	
	def build_initial_window(self, blueBotName, orngBotName):
		
		# Everything starts at 2,2 (I can't figure out why tkinter pains me but it does...)
		
		self.p1decel = self.canvas.create_rectangle(4, 257, 36, 266, fill='lightcoral')
		self.p1acel = self.canvas.create_rectangle(36, 257, 68, 266, fill='pale green')
		self.p2decel = self.canvas.create_rectangle(183, 257, 215, 266, fill='lightcoral')
		self.p2acel = self.canvas.create_rectangle(215, 257, 247, 266, fill='pale green')
		
		self.p1a = self.canvas.create_oval(2, 240, 18, 255, fill='pale green')
		self.p1b = self.canvas.create_oval(21, 240, 35, 255, fill='lightcoral')
		self.p1x = self.canvas.create_oval(38, 240, 52, 255, fill='steelblue1')
		
		self.p2a = self.canvas.create_oval(199, 240, 213, 255, fill='pale green')
		self.p2b = self.canvas.create_oval(216, 240, 231, 255, fill='lightcoral')
		self.p2x = self.canvas.create_oval(233, 240, 247, 255, fill='steelblue1')
		
		self.canvas.create_image(36, 300, image=self.stickzone)
		self.canvas.create_image(216, 300, image=self.stickzone)
		self.canvas.create_image(126, 168, image=self.background)
		
		self.p1marker = self.canvas.create_image(36, 300, image=self.marker)
		self.p2marker = self.canvas.create_image(216, 300, image=self.marker)
		
		self.canvas.create_text(126, 13, text=blueBotName, fill='blue', font=("Calibri Bold", 13))
		self.canvas.create_text(126, 56, text=orngBotName, fill='darkorange2', font=("Calibri Bold", 13))
		
		self.canvas.create_text(126, 245, text="Score")
		self.canvas.create_text(126, 261, text="Goals")
		self.canvas.create_text(126, 277, text="Own Goals")
		self.canvas.create_text(126, 293, text="Shots")
		self.canvas.create_text(126, 309, text="Saves")
		self.canvas.create_text(126, 325, text="Demolitions")
		
		self.p1score = self.canvas.create_text(72, 245, text="1111")
		self.p1goals = self.canvas.create_text(79, 261, text="10")
		self.p1owngoals = self.canvas.create_text(79, 277, text="11")
		self.p1shots = self.canvas.create_text(79, 293, text="12")
		self.p1saves = self.canvas.create_text(79, 309, text="13")
		self.p1demos = self.canvas.create_text(79, 325, text="14")
		
		self.p2score = self.canvas.create_text(180, 245, text="2222")
		self.p2goals = self.canvas.create_text(172, 261, text="20")
		self.p2owngoals = self.canvas.create_text(172, 277, text="21")
		self.p2shots = self.canvas.create_text(172, 293, text="22")
		self.p2saves = self.canvas.create_text(172, 309, text="23")
		self.p2demos = self.canvas.create_text(172, 325, text="24")
		
		self.p1scoreboardscore = self.canvas.create_text(91, 34, text="99", fill='blue')
		self.p2scoreboardscore = self.canvas.create_text(161, 34, text="69", fill='darkorange2')
		self.timeremaining = self.canvas.create_text(126, 34, text="500.24")
		
		self.blue = self.canvas.create_rectangle(126, 154, 130, 158, fill='blue', outline='blue')
		self.orange = self.canvas.create_rectangle(126, 154, 130, 158, fill='darkorange2', outline='darkorange2')
		self.ball = self.canvas.create_rectangle(126, 154, 130, 158, fill='white', outline='white')

		self.canvas.pack()

		# Display
		self.root.update_idletasks()
		self.root.update()

	# FUNCTION TO UPDATE
	def UpdateDisplay(self, sharedValue):
	
		gameTickPacket = sharedValue.GameTickPacket
		
		team1Blue = (gameTickPacket.gamecars[0].Team == 0)
		if team1Blue:
			blueIndex = 0
			orngIndex = 1
		else:
			blueIndex = 1
			orngIndex = 0
			
		# If overtime set text color to red
		if (gameTickPacket.gameInfo.bOverTime):
			self.canvas.itemconfig(self.timeremaining, fill='red')
		else:
			self.canvas.itemconfig(self.timeremaining, fill='black')
		
		# First update all string values
		self.canvas.itemconfig(self.timeremaining, text=round(gameTickPacket.gameInfo.GameTimeRemaining,2))
		self.canvas.itemconfig(self.p1scoreboardscore, text=(gameTickPacket.gamecars[blueIndex].Score.Goals + gameTickPacket.gamecars[orngIndex].Score.OwnGoals))
		self.canvas.itemconfig(self.p2scoreboardscore, text=(gameTickPacket.gamecars[orngIndex].Score.Goals + gameTickPacket.gamecars[blueIndex].Score.OwnGoals))
		self.canvas.itemconfig(self.p1score, text=gameTickPacket.gamecars[blueIndex].Score.Score)
		self.canvas.itemconfig(self.p2score, text=gameTickPacket.gamecars[orngIndex].Score.Score)
		self.canvas.itemconfig(self.p1goals, text=gameTickPacket.gamecars[blueIndex].Score.Goals)
		self.canvas.itemconfig(self.p2goals, text=gameTickPacket.gamecars[orngIndex].Score.Goals)
		self.canvas.itemconfig(self.p1owngoals, text=gameTickPacket.gamecars[blueIndex].Score.OwnGoals)
		self.canvas.itemconfig(self.p2owngoals, text=gameTickPacket.gamecars[orngIndex].Score.OwnGoals)
		self.canvas.itemconfig(self.p1saves, text=gameTickPacket.gamecars[blueIndex].Score.Saves)
		self.canvas.itemconfig(self.p2saves, text=gameTickPacket.gamecars[orngIndex].Score.Saves)
		self.canvas.itemconfig(self.p1shots, text=gameTickPacket.gamecars[blueIndex].Score.Shots)
		self.canvas.itemconfig(self.p2shots, text=gameTickPacket.gamecars[orngIndex].Score.Shots)
		self.canvas.itemconfig(self.p1demos, text=gameTickPacket.gamecars[blueIndex].Score.Demolitions)
		self.canvas.itemconfig(self.p2demos, text=gameTickPacket.gamecars[orngIndex].Score.Demolitions)
		
		# Move blue, orange, ball
		blueY_X = int((gameTickPacket.gamecars[blueIndex].Location.Y + (self.UU_FIELD_WIDTH / 2)) / (self.UU_FIELD_WIDTH / self.FIELD_WIDTH)) + 3
		blueX_Y = int((-1 * gameTickPacket.gamecars[blueIndex].Location.X + (self.UU_FIELD_HEIGHT / 2)) / (self.UU_FIELD_HEIGHT / self.FIELD_HEIGHT)) + 72
		self.canvas.coords(self.blue, blueY_X, blueX_Y, blueY_X + self.PLAYER_PIXEL_SIZE, blueX_Y + self.PLAYER_PIXEL_SIZE)
		
		orngY_X = int((gameTickPacket.gamecars[orngIndex].Location.Y + (self.UU_FIELD_WIDTH / 2)) / (self.UU_FIELD_WIDTH / self.FIELD_WIDTH)) + 3
		orngX_Y = int((-1 * gameTickPacket.gamecars[orngIndex].Location.X + (self.UU_FIELD_HEIGHT / 2)) / (self.UU_FIELD_HEIGHT / self.FIELD_HEIGHT)) + 72
		self.canvas.coords(self.orange, orngY_X, orngX_Y, orngY_X + self.PLAYER_PIXEL_SIZE, orngX_Y + self.PLAYER_PIXEL_SIZE)
		
		ballY_X = int((gameTickPacket.gameball.Location.Y + (self.UU_FIELD_WIDTH / 2)) / (self.UU_FIELD_WIDTH / self.FIELD_WIDTH)) + 3
		ballX_Y = int((-1 * gameTickPacket.gameball.Location.X + (self.UU_FIELD_HEIGHT / 2)) / (self.UU_FIELD_HEIGHT / self.FIELD_HEIGHT)) + 72
		self.canvas.coords(self.ball, ballY_X, ballX_Y, ballY_X + self.PLAYER_PIXEL_SIZE, ballX_Y + self.PLAYER_PIXEL_SIZE)
		
		# Now refresh gui
		self.root.update_idletasks()
		self.root.update()
		
	def UpdateKeyPresses(self, output1, output2):
	
		self.canvas.coords(self.p1marker, output1[0] * 62 / 32767 + 5, output1[1] * 62 / 32767 + 268)
		self.canvas.coords(self.p1acel, (36, 257, (36 + output1[2] * 32 / 32767), 266))
		self.canvas.coords(self.p1decel, (36 - output1[3] * 32 / 32767), 257, 36, 266)
	
		if output1[4] == 0:
			self.canvas.itemconfig(self.p1a, fill='white')
		else:
			self.canvas.itemconfig(self.p1a, fill='pale green')
			
		if output1[5] == 0:
			self.canvas.itemconfig(self.p1b, fill='white')
		else:
			self.canvas.itemconfig(self.p1b, fill='lightcoral')
			
		if output1[6] == 0:
			self.canvas.itemconfig(self.p1x, fill='white')
		else:
			self.canvas.itemconfig(self.p1x, fill='steelblue1')
			
		self.canvas.coords(self.p2marker, output2[0] * 62 / 32767 + 184, output2[1] * 62 / 32767 + 268)
		self.canvas.coords(self.p2acel, (215, 257, (215 + output2[2] * 32 / 32767), 266))
		self.canvas.coords(self.p2decel, (215 - output2[3] * 32 / 32767), 257, 215, 266)
	
		if output2[4] == 0:
			self.canvas.itemconfig(self.p2a, fill='white')
		else:
			self.canvas.itemconfig(self.p2a, fill='pale green')
			
		if output2[5] == 0:
			self.canvas.itemconfig(self.p2b, fill='white')
		else:
			self.canvas.itemconfig(self.p2b, fill='lightcoral')
			
		if output2[6] == 0:
			self.canvas.itemconfig(self.p2x, fill='white')
		else:
			self.canvas.itemconfig(self.p2x, fill='steelblue1')
		
		# Now refresh gui
		self.root.update_idletasks()
		self.root.update()
