from tkinter import *
from math import sin

class real_time_display:

	# Define Constants
	FIELD_WIDTH = 244
	FIELD_HEIGHT = 164
	PLAYER_LABEL_WIDTH = 11
	PLAYER_VALUE_WIDTH = 14
	OUTPUT_WIDTH = 28
	SCOREBOARD_SCORE_WIDTH = 2
	GOAL_DEPTH = 10
	GOAL_LENGTH = 36
	PLAYER_PIXEL_SIZE = 4
	
	WINDOW_WIDTH_HALF = 19
	WINDOW_WIDTH_THIRDS = 12
	STAT_LABEL_WIDTH = 10
	STAT_SEPARATOR_WIDTH = 1
	STAT_VALUE_WIDTH = 4
	
	# Variables
	root = Tk()
	
	blueScore = StringVar(value="Blue")
	orngScore = StringVar(value="Orange")
	bluePoints = StringVar(value="123")
	orngPoints = StringVar(value="456")
	blueGoals = StringVar(value="CC")
	orngGoals = StringVar(value="DD")
	blueShots = StringVar(value="EE")
	orngShots = StringVar(value="FF")
	blueOwnGoals = StringVar(value="G")
	orngOwnGoals = StringVar(value="H")
	blueSaves = StringVar(value="II")
	orngSaves = StringVar(value="JJ")
	blueDemos = StringVar(value="KK")
	orngDemos = StringVar(value="LL")
	blueLR = StringVar(value="AAAAA")
	blueUD = StringVar(value="BBBBB")
	blueF = StringVar(value="CCCCC")
	blueR = StringVar(value="DDDDD")
	blueA = StringVar(value="E")
	blueB = StringVar(value="F")
	blueX = StringVar(value="G")
	orngLR = StringVar(value="AAAAA")
	orngUD = StringVar(value="BBBBB")
	orngF = StringVar(value="CCCCC")
	orngR = StringVar(value="DDDDD")
	orngA = StringVar(value="E")
	orngB = StringVar(value="F")
	orngX = StringVar(value="G")
	timeRemaining = StringVar(value="time")
	
	field = PhotoImage(width=FIELD_WIDTH, height=FIELD_HEIGHT)
	
	lastBlueX = 50
	lastBlueY = 50
	lastOrngX = 50
	lastOrngY = 50
	lastBallX = 50
	lastBallY = 50
	
	windowFrame = Frame(root)
	timeRemainingFrame = Frame(windowFrame)
	overtimeColorChangeLabel = Label(timeRemainingFrame, textvariable=timeRemaining, pady=0, borderwidth=0, font=("Calibri Regular", 8), width=WINDOW_WIDTH_HALF)
	
	def build_initial_window(self, blueBotName, orngBotName):
		
		# Set up frames
		windowFrame = self.windowFrame
		windowFrame.pack()
		
		botNameFrame = Frame(windowFrame)
		botNameFrame.pack()

		scoreboardFrame = Frame(windowFrame)
		scoreboardFrame.pack()
		
		self.timeRemainingFrame.pack()

		middleFrame = Frame(windowFrame)
		middleFrame.pack()
		
		fieldCanvas = Canvas(middleFrame, width=(self.FIELD_WIDTH), height=(self.FIELD_HEIGHT), bg="lightgreen")
		fieldCanvas.pack(side=TOP)
		
		statBoardFrame = Frame(windowFrame)
		statBoardFrame.pack()
		
		statLabelColumn1 = Frame(statBoardFrame)
		statLabelColumn1.pack(side=LEFT, fill=BOTH)
		
		statValueColumn1 = Frame(statBoardFrame)
		statValueColumn1.pack(side=LEFT, fill=BOTH)
		
		statSeparatorColumn1 = Frame(statBoardFrame)
		statSeparatorColumn1.pack(side=LEFT, fill=BOTH)
		
		statValueColumn2 = Frame(statBoardFrame)
		statValueColumn2.pack(side=LEFT, fill=BOTH)
		
		statLabelColumn2 = Frame(statBoardFrame)
		statLabelColumn2.pack(side=LEFT, fill=BOTH)
		
		statValueColumn3 = Frame(statBoardFrame)
		statValueColumn3.pack(side=LEFT, fill=BOTH)
		
		statSeparatorColumn2 = Frame(statBoardFrame)
		statSeparatorColumn2.pack(side=LEFT, fill=BOTH)
		
		statValueColumn4 = Frame(statBoardFrame)
		statValueColumn4.pack(side=LEFT, fill=BOTH)
		
		spacerFrame = Frame(windowFrame)
		spacerFrame.pack()

		controllerFrame = Frame(windowFrame)
		controllerFrame.pack()
		
		controllerLabel = Frame(controllerFrame)
		controllerLabel.pack(side=LEFT, fill=BOTH)
		
		controllerBlue = Frame(controllerFrame)
		controllerBlue.pack(side=LEFT, fill=BOTH)
		
		controllerOrng = Frame(controllerFrame)
		controllerOrng.pack(side=LEFT, fill=BOTH)
		
		# BOT NAME FRAME
		Label(botNameFrame, text=blueBotName, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Bold", 13)).pack()
		Label(botNameFrame, text="vs.", padx=0, pady=0, borderwidth=0, font=("Calibri Bold Italic", 10)).pack()
		Label(botNameFrame, text=orngBotName, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Bold", 13)).pack()
		
		# SCOREBOARD FRAME
		Label(scoreboardFrame, textvariable=self.blueScore, fg="blue", pady=0, borderwidth=0, font=("Calibri Regular", 8)).pack(side=LEFT)
		Label(scoreboardFrame, text="-", pady=0, borderwidth=0, font=("Calibri Regular", 8)).pack(side=LEFT)
		Label(scoreboardFrame, textvariable=self.orngScore, fg="darkorange2", pady=0, borderwidth=0, font=("Calibri Regular", 8)).pack(side=LEFT)
		
		# TIME REMAINING FRAME
		Label(self.timeRemainingFrame, text="Time Remaining: ", pady=0, borderwidth=0, font=("Calibri Regular", 8), width=self.WINDOW_WIDTH_HALF).pack(side=LEFT)
		self.overtimeColorChangeLabel.pack(side=LEFT)

		# DRAW INITIAL FIELD
		fieldCanvas.create_image(2, 2, anchor="nw", image=self.field, state="normal") # Why does this need to start at 2,2 and not 0,0 to align with the canvas? I have no idea, probably some border somewhere or something.

		for x in range(self.GOAL_DEPTH):
			for y in range(int((self.FIELD_HEIGHT / 2) - (self.GOAL_LENGTH / 2))):
				self.field.put("dimgrey", (x,y))
				
		for x in range(self.GOAL_DEPTH):
			for y in range(int(self.FIELD_HEIGHT - (self.FIELD_HEIGHT / 2) + (self.GOAL_LENGTH / 2)), self.FIELD_HEIGHT):
				self.field.put("dimgrey", (x,y))
				
		for x in range((self.FIELD_WIDTH - self.GOAL_DEPTH), self.FIELD_WIDTH):
			for y in range(int((self.FIELD_HEIGHT / 2) - (self.GOAL_LENGTH / 2))):
				self.field.put("dimgrey", (x,y))
				
		for x in range((self.FIELD_WIDTH - self.GOAL_DEPTH), self.FIELD_WIDTH):
			for y in range(int(self.FIELD_HEIGHT - (self.FIELD_HEIGHT / 2) + (self.GOAL_LENGTH / 2)), self.FIELD_HEIGHT):
				self.field.put("dimgrey", (x,y))
				
		# STAT BOARD FRAME
		Label(statLabelColumn1, text="Score:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_LABEL_WIDTH).pack()
		Label(statLabelColumn1, text="Goals:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_LABEL_WIDTH).pack()
		Label(statLabelColumn1, text="Own Goals:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_LABEL_WIDTH).pack()
		
		Label(statValueColumn1, textvariable=self.bluePoints, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="right", anchor="e", width=self.STAT_VALUE_WIDTH).pack()
		Label(statValueColumn1, textvariable=self.blueGoals, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="right", anchor="e", width=self.STAT_VALUE_WIDTH).pack()
		Label(statValueColumn1, textvariable=self.blueOwnGoals, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="right", anchor="e", width=self.STAT_VALUE_WIDTH).pack()
		
		Label(statSeparatorColumn1, text="/", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_SEPARATOR_WIDTH).pack()
		Label(statSeparatorColumn1, text="/", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_SEPARATOR_WIDTH).pack()
		Label(statSeparatorColumn1, text="/", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_SEPARATOR_WIDTH).pack()
		
		Label(statValueColumn2, textvariable=self.orngPoints, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_VALUE_WIDTH).pack()
		Label(statValueColumn2, textvariable=self.orngGoals, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_VALUE_WIDTH).pack()
		Label(statValueColumn2, textvariable=self.orngOwnGoals, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_VALUE_WIDTH).pack()
		
		Label(statLabelColumn2, text="Shots:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_LABEL_WIDTH).pack()
		Label(statLabelColumn2, text="Saves:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_LABEL_WIDTH).pack()
		Label(statLabelColumn2, text="Demolition:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_LABEL_WIDTH).pack()
		
		Label(statValueColumn3, textvariable=self.blueShots, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="right", anchor="e", width=self.STAT_VALUE_WIDTH).pack()
		Label(statValueColumn3, textvariable=self.blueSaves, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="right", anchor="e", width=self.STAT_VALUE_WIDTH).pack()
		Label(statValueColumn3, textvariable=self.blueDemos, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="right", anchor="e", width=self.STAT_VALUE_WIDTH).pack()
		
		Label(statSeparatorColumn2, text="/", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_SEPARATOR_WIDTH).pack()
		Label(statSeparatorColumn2, text="/", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_SEPARATOR_WIDTH).pack()
		Label(statSeparatorColumn2, text="/", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_SEPARATOR_WIDTH).pack()
		
		Label(statValueColumn4, textvariable=self.orngShots, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_VALUE_WIDTH).pack()
		Label(statValueColumn4, textvariable=self.orngSaves, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_VALUE_WIDTH).pack()
		Label(statValueColumn4, textvariable=self.orngDemos, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_VALUE_WIDTH).pack()
		
		# SPACER FRAME
		Label(spacerFrame, text=" ", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.STAT_SEPARATOR_WIDTH).pack()

		# CONTROLLER PRESS FRAME
		Label(controllerLabel, text="Left/Right:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerLabel, text="Up/Down:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerLabel, text="Forward:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerLabel, text="Reverse:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerLabel, text="A:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerLabel, text="B:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerLabel, text="X:", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		
		Label(controllerBlue, textvariable=self.blueLR, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerBlue, textvariable=self.blueUD, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerBlue, textvariable=self.blueF, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerBlue, textvariable=self.blueR, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerBlue, textvariable=self.blueA, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerBlue, textvariable=self.blueB, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerBlue, textvariable=self.blueX, fg="blue", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		
		Label(controllerOrng, textvariable=self.orngLR, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerOrng, textvariable=self.orngUD, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerOrng, textvariable=self.orngF, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerOrng, textvariable=self.orngR, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerOrng, textvariable=self.orngA, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerOrng, textvariable=self.orngB, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()
		Label(controllerOrng, textvariable=self.orngX, fg="darkorange2", padx=0, pady=0, borderwidth=0, font=("Calibri Regular", 8), justify="left", anchor="w", width=self.WINDOW_WIDTH_THIRDS).pack()

		# Display
		self.root.update_idletasks()
		self.root.update()
		
	def sanity_check_x(self, x):
		return ((x >= 0) and (x < self.FIELD_HEIGHT)) # need to run these for 2d map display so not plotting random illegal points after goal scored / demo
		
	def sanity_check_z(self, z):
		return ((z >= 0) and (z < self.FIELD_WIDTH))

	# FUNCTION TO UPDATE
	def UpdateDisplay(self, sharedValue):
	
		gameTickPacket = sharedValue.GameTickPacket
		
		UU_TO_GV = 50
		
		team1Blue = (gameTickPacket.gamecars[0].Team == 0)
		if team1Blue:
			blueIndex = 0
			orngIndex = 1
		else:
			blueIndex = 1
			orngIndex = 0
			
		# If overtime set text color to red
		if (gameTickPacket.gameInfo.bOverTime):
			self.overtimeColorChangeLabel.config(fg="red")
		else:
			self.overtimeColorChangeLabel.config(fg="black")
		
		# First update all string values
		self.timeRemaining.set(round(gameTickPacket.gameInfo.GameTimeRemaining,2))
		self.blueScore.set(gameTickPacket.gamecars[blueIndex].Score.Goals + gameTickPacket.gamecars[orngIndex].Score.OwnGoals)
		self.orngScore.set(gameTickPacket.gamecars[orngIndex].Score.Goals + gameTickPacket.gamecars[blueIndex].Score.OwnGoals)
		self.orngDemos.set(gameTickPacket.gamecars[orngIndex].Score.Demolitions) # Demos by orng, not when orng gets demo!
		self.blueDemos.set(gameTickPacket.gamecars[blueIndex].Score.Demolitions)
		self.bluePoints.set(gameTickPacket.gamecars[blueIndex].Score.Score)
		self.orngPoints.set(gameTickPacket.gamecars[orngIndex].Score.Score)
		self.blueGoals.set(gameTickPacket.gamecars[blueIndex].Score.Goals)
		self.blueSaves.set(gameTickPacket.gamecars[blueIndex].Score.Saves)
		self.blueShots.set(gameTickPacket.gamecars[blueIndex].Score.Shots)
		self.orngGoals.set(gameTickPacket.gamecars[orngIndex].Score.Goals)
		self.orngSaves.set(gameTickPacket.gamecars[orngIndex].Score.Saves)
		self.orngShots.set(gameTickPacket.gamecars[orngIndex].Score.Shots)
		self.blueOwnGoals.set(gameTickPacket.gamecars[blueIndex].Score.OwnGoals)
		self.orngOwnGoals.set(gameTickPacket.gamecars[orngIndex].Score.OwnGoals)
		
		# Draw blue player
		if (self.sanity_check_x(self.lastBlueX) and self.sanity_check_z(self.lastBlueY)):
			for i in range(self.lastBlueY, self.lastBlueY + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastBlueX, self.lastBlueX + self.PLAYER_PIXEL_SIZE):
					self.field.put("lightgreen", (i, j))
		self.lastBlueX = int( (-1) * gameTickPacket.gamecars[blueIndex].Location.X / UU_TO_GV + (self.FIELD_HEIGHT / 2))
		self.lastBlueY = int(gameTickPacket.gamecars[blueIndex].Location.Y / UU_TO_GV + (self.FIELD_WIDTH / 2))
		if (self.sanity_check_x(self.lastBlueX) and self.sanity_check_z(self.lastBlueY)):
			for i in range(self.lastBlueY, self.lastBlueY + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastBlueX, self.lastBlueX + self.PLAYER_PIXEL_SIZE):
					self.field.put("blue", (i, j))
				
		# Draw orange player
		if (self.sanity_check_x(self.lastOrngX) and self.sanity_check_z(self.lastOrngY)):
			for i in range(self.lastOrngY, self.lastOrngY + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastOrngX, self.lastOrngX + self.PLAYER_PIXEL_SIZE):
					self.field.put("lightgreen", (i, j))
		self.lastOrngX = int( (-1) * gameTickPacket.gamecars[orngIndex].Location.X / UU_TO_GV + (self.FIELD_HEIGHT / 2))
		self.lastOrngY = int(gameTickPacket.gamecars[orngIndex].Location.Y / UU_TO_GV + (self.FIELD_WIDTH / 2))
		if (self.sanity_check_x(self.lastOrngX) and self.sanity_check_z(self.lastOrngY)):
			for i in range(self.lastOrngY, self.lastOrngY + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastOrngX, self.lastOrngX + self.PLAYER_PIXEL_SIZE):
					self.field.put("darkorange2", (i, j))
				
		# Draw ball
		if (self.sanity_check_x(self.lastBallX) and self.sanity_check_z(self.lastBallY)):
			for i in range(self.lastBallY, self.lastBallY + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastBallX, self.lastBallX + self.PLAYER_PIXEL_SIZE):
					self.field.put("lightgreen", (i, j))
		self.lastBallX = int( (-1) * gameTickPacket.gameball.Location.X / UU_TO_GV + (self.FIELD_HEIGHT / 2))
		self.lastBallY = int(gameTickPacket.gameball.Location.Y / UU_TO_GV + (self.FIELD_WIDTH / 2))
		if (self.sanity_check_x(self.lastBallX) and self.sanity_check_z(self.lastBallY)):
			for i in range(self.lastBallY, self.lastBallY + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastBallX, self.lastBallX + self.PLAYER_PIXEL_SIZE):
					self.field.put("white", (i, j))
		
		# Now refresh gui
		self.root.update_idletasks()
		self.root.update()
		
	def UpdateKeyPresses(self, output1, output2):
		self.blueLR.set(output1[0])
		self.blueUD.set(output1[1])
		self.blueF.set(output1[2])
		self.blueR.set(output1[3])
		self.blueA.set(output1[4])
		self.blueB.set(output1[5])
		self.blueX.set(output1[6])
		
		self.orngLR.set(output2[0])
		self.orngUD.set(output2[1])
		self.orngF.set(output2[2])
		self.orngR.set(output2[3])
		self.orngA.set(output2[4])
		self.orngB.set(output2[5])
		self.orngX.set(output2[6])
		
		# Now refresh gui
		self.root.update_idletasks()
		self.root.update()
