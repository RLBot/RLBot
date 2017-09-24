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
	
	canvas = Canvas(root, height=338, width=248, borderwidth=0)
	
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
	
	PLAYER_PIXEL_SIZE = 3
	FIELD_WIDTH = 242
	FIELD_HEIGHT = 162
	UU_FIELD_WIDTH = 11880
	UU_FIELD_HEIGHT = 8160
	
	def build_initial_window(self, blueBotName, orngBotName):
		
		# Everything starts at 2,2 (I can't figure out why tkinter pains me but it does...)
		
		self.canvas.create_rectangle(0, 0, 248, 338, fill='#9c9c9c') # Put a rectangle behind the acceleration/deceleration
		
		self.p1decel = self.canvas.create_rectangle(4, 262, 36, 271, fill='lightcoral')
		self.p1acel = self.canvas.create_rectangle(36, 262, 68, 271, fill='pale green')
		self.p2decel = self.canvas.create_rectangle(183, 262, 215, 271, fill='lightcoral')
		self.p2acel = self.canvas.create_rectangle(215, 262, 247, 271, fill='pale green')
		
		self.p1a = self.canvas.create_oval(2, 244, 18, 259, fill='pale green')
		self.p1b = self.canvas.create_oval(21, 244, 35, 259, fill='lightcoral')
		self.p1x = self.canvas.create_oval(38, 244, 52, 259, fill='steelblue1')
		
		self.p2a = self.canvas.create_oval(199, 238, 213, 259, fill='pale green')
		self.p2b = self.canvas.create_oval(216, 238, 231, 259, fill='lightcoral')
		self.p2x = self.canvas.create_oval(233, 238, 247, 259, fill='steelblue1')
		
		self.canvas.create_image(36, 305, image=self.stickzone)
		self.canvas.create_image(215, 305, image=self.stickzone)
		
		self.p1marker = self.canvas.create_image(36, 305, image=self.marker)
		self.p2marker = self.canvas.create_image(216, 305, image=self.marker)
		
		self.canvas.create_image(126, 171, image=self.background)
		
		self.canvas.create_text(126, 13, text=blueBotName, fill='blue', font=("Calibri Bold", 13))
		self.canvas.create_text(126, 56, text=orngBotName, fill='darkorange2', font=("Calibri Bold", 13))
		
		self.canvas.create_text(126, 251, text="Score", font=("sans", 10))
		self.canvas.create_text(126, 267, text="Goals", font=("sans", 10))
		self.canvas.create_text(126, 283, text="Own Goals", font=("sans", 10))
		self.canvas.create_text(126, 299, text="Shots", font=("sans", 10))
		self.canvas.create_text(126, 315, text="Saves", font=("sans", 10))
		self.canvas.create_text(126, 331, text="Demolitions", font=("sans", 10))
		
		self.p1score = self.canvas.create_text(86, 251, text="1111", anchor='e', font=("sans", 10))
		self.p1goals = self.canvas.create_text(86, 267, text="10", anchor='e',font=("sans", 10))
		self.p1owngoals = self.canvas.create_text(86, 283, text="11", anchor='e', font=("sans", 10))
		self.p1shots = self.canvas.create_text(86, 299, text="12", anchor='e', font=("sans", 10))
		self.p1saves = self.canvas.create_text(86, 315, text="13",anchor='e', font=("sans", 10))
		self.p1demos = self.canvas.create_text(86, 331, text="14", anchor='e', font=("sans", 10))
		
		self.p2score = self.canvas.create_text(166, 251, text="2222", anchor='w', font=("sans", 10))
		self.p2goals = self.canvas.create_text(166, 267, text="20", anchor='w', font=("sans", 10))
		self.p2owngoals = self.canvas.create_text(166, 283, text="21", anchor='w', font=("sans", 10))
		self.p2shots = self.canvas.create_text(166, 299, text="22", anchor='w', font=("sans", 10))
		self.p2saves = self.canvas.create_text(166, 315, text="23", anchor='w', font=("sans", 10))
		self.p2demos = self.canvas.create_text(166, 331, text="24", anchor='w', font=("sans", 10))
		
		self.p1scoreboardscore = self.canvas.create_text(88, 34, text="99", fill='blue', font=("Calibri Bold", 13))
		self.p2scoreboardscore = self.canvas.create_text(164, 34, text="69", fill='darkorange2', font=("Calibri Bold", 13))
		self.timeremaining = self.canvas.create_text(126, 34, text="500.24", font=("Calibri Bold", 13))
		
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
		timeRemaining = gameTickPacket.gameInfo.GameTimeRemaining
		if timeRemaining >= 60:
			self.canvas.itemconfig(self.timeremaining, text=("%d:%02d" % (int(timeRemaining / 60), (int(timeRemaining) % 60))))
		else:
			self.canvas.itemconfig(self.timeremaining, text=("%.2f" % timeRemaining))
			
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
	
		self.canvas.coords(self.p1marker, output1[0] * 62 / 32767 + 5, output1[1] * 62 / 32767 + 274)
		self.canvas.coords(self.p1acel, (36, 261, (36 + output1[2] * 32 / 32767), 270))
		self.canvas.coords(self.p1decel, (36 - output1[3] * 32 / 32767), 261, 36, 270)
	
		if output1[4] == 0:
			self.canvas.itemconfig(self.p1a, fill='#9c9c9c')
		else:
			self.canvas.itemconfig(self.p1a, fill='pale green')
			
		if output1[5] == 0:
			self.canvas.itemconfig(self.p1b, fill='#9c9c9c')
		else:
			self.canvas.itemconfig(self.p1b, fill='lightcoral')
			
		if output1[6] == 0:
			self.canvas.itemconfig(self.p1x, fill='#9c9c9c')
		else:
			self.canvas.itemconfig(self.p1x, fill='steelblue1')
			
		self.canvas.coords(self.p2marker, output2[0] * 62 / 32767 + 184, output2[1] * 62 / 32767 + 274)
		self.canvas.coords(self.p2acel, (215, 261, (215 + output2[2] * 32 / 32767), 270))
		self.canvas.coords(self.p2decel, (215 - output2[3] * 32 / 32767), 261, 215, 270)
	
		if output2[4] == 0:
			self.canvas.itemconfig(self.p2a, fill='#9c9c9c')
		else:
			self.canvas.itemconfig(self.p2a, fill='pale green')
			
		if output2[5] == 0:
			self.canvas.itemconfig(self.p2b, fill='#9c9c9c')
		else:
			self.canvas.itemconfig(self.p2b, fill='lightcoral')
			
		if output2[6] == 0:
			self.canvas.itemconfig(self.p2x, fill='#9c9c9c')
		else:
			self.canvas.itemconfig(self.p2x, fill='steelblue1')
		
		# Now refresh gui
		self.root.update_idletasks()
		self.root.update()
