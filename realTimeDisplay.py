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
	
	# Variables
	root = Tk()
	
	blueScore = StringVar(value="BLUE")
	orngScore = StringVar(value="Orange")
	bluePoints = StringVar(value="A")
	orngPoints = StringVar(value="B")
	blueGoals = StringVar(value="C")
	orngGoals = StringVar(value="D")
	blueShots = StringVar(value="E")
	orngShots = StringVar(value="F")
	blueSaves = StringVar(value="I")
	orngSaves = StringVar(value="J")
	blueDemos = StringVar(value="K")
	orngDemos = StringVar(value="L")
	blueXZYPos = StringVar(value="p(x,z,y)")
	blueXZYVel = StringVar(value="v(x,z,y)")
	blueBoost = StringVar(value="boost")
	orngBoost = StringVar(value="boost")
	blueRot1 = StringVar(value="rot1")
	blueRot2 = StringVar(value="rot2")
	blueRot3 = StringVar(value="rot3")
	blueRot4 = StringVar(value="rot4")
	blueRot5 = StringVar(value="rot5")
	blueRot6 = StringVar(value="rot6")
	blueRot7 = StringVar(value="rot7")
	blueRot8 = StringVar(value="rot8")
	blueRot9 = StringVar(value="rot9")
	orngXZYPos = StringVar(value="p(x,z,y)")
	orngXZYVel = StringVar(value="v(x,z,y)")
	orngRot1 = StringVar(value="rot1")
	orngRot2 = StringVar(value="rot2")
	orngRot3 = StringVar(value="rot3")
	orngRot4 = StringVar(value="rot4")
	orngRot5 = StringVar(value="rot5")
	orngRot6 = StringVar(value="rot6")
	orngRot7 = StringVar(value="rot7")
	orngRot8 = StringVar(value="rot8")
	orngRot9 = StringVar(value="rot9")
	ballXZYPos = StringVar(value="p(x,z,y)")
	ballXZYVel = StringVar(value="v(x,z,y)")
	blueOutput = StringVar(value="Blue Output")
	orngOutput = StringVar(value="Blue Output")
	
	field = PhotoImage(width=FIELD_WIDTH, height=FIELD_HEIGHT)
	
	lastBlueX = 50
	lastBlueZ = 50
	lastOrngX = 50
	lastOrngZ = 50
	lastBallX = 50
	lastBallZ = 50
	
	def build_initial_window(self, blueBotName, orngBotName):
		
		# Set up frames
		windowFrame = Frame(self.root)
		windowFrame.pack()

		scoreboardFrame = Frame(windowFrame)
		scoreboardFrame.pack()

		statBoardFrame = Frame(windowFrame)
		statBoardFrame.pack()

		middleFrame = Frame(windowFrame)
		middleFrame.pack()
		
		fieldCanvas = Canvas(middleFrame, width=(self.FIELD_WIDTH), height=(self.FIELD_HEIGHT), bg="lightgreen")
		fieldCanvas.pack(side=TOP)

		blueLabelFrame = Frame(middleFrame)
		blueLabelFrame.pack(side=LEFT, fill=BOTH)

		blueValueFrame = Frame(middleFrame)
		blueValueFrame.pack(side=LEFT, fill=BOTH)

		orngLabelFrame = Frame(middleFrame)
		orngLabelFrame.pack(side=LEFT, fill=BOTH)

		orngValueFrame = Frame(middleFrame)
		orngValueFrame.pack(side=LEFT, fill=BOTH)

		blueControllerFrame = Frame(windowFrame)
		blueControllerFrame.pack()

		blueControllerLabel = Frame(blueControllerFrame)
		blueControllerLabel.pack(side=LEFT, fill=BOTH)

		blueControllerValue = Frame(blueControllerFrame)
		blueControllerValue.pack(side=LEFT, fill=BOTH)

		orngControllerFrame = Frame(windowFrame)
		orngControllerFrame.pack()

		orngControllerLabel = Frame(orngControllerFrame)
		orngControllerLabel.pack(side=LEFT, fill=BOTH)

		orngControllerValue = Frame(orngControllerFrame)
		orngControllerValue.pack(side=LEFT, fill=BOTH)

		# SCOREBOARD
		Label(scoreboardFrame, text=blueBotName, fg="blue").pack(side=LEFT)
		Label(scoreboardFrame, textvariable=self.blueScore, fg="blue").pack(side=LEFT)
		Label(scoreboardFrame, text="-").pack(side=LEFT)
		Label(scoreboardFrame, textvariable=self.orngScore, fg="darkorange2").pack(side=LEFT)
		Label(scoreboardFrame, text=orngBotName, fg="darkorange2").pack(side=LEFT)

		# STATS
		Label(statBoardFrame, text="Points:").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.bluePoints, fg="blue").pack(side=LEFT)
		Label(statBoardFrame, text="/").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.orngPoints, fg="darkorange2").pack(side=LEFT)

		Label(statBoardFrame, text="Goals:").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.blueGoals, fg="blue").pack(side=LEFT)
		Label(statBoardFrame, text="/").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.orngGoals, fg="darkorange2").pack(side=LEFT)
		
		Label(statBoardFrame, text="Shots:").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.blueShots, fg="blue").pack(side=LEFT)
		Label(statBoardFrame, text="/").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.orngShots, fg="darkorange2").pack(side=LEFT)

		Label(statBoardFrame, text="Saves:").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.blueSaves, fg="blue").pack(side=LEFT)
		Label(statBoardFrame, text="/").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.orngSaves, fg="darkorange2").pack(side=LEFT)

		Label(statBoardFrame, text="Demolitions:").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.blueDemos, fg="blue").pack(side=LEFT)
		Label(statBoardFrame, text="/").pack(side=LEFT)
		Label(statBoardFrame, textvariable=self.orngDemos, fg="darkorange2").pack(side=LEFT)

		# MIDDLE FRAME

		# -- Create Labels --
		Label(blueLabelFrame, text="Position (x,z,y):", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Velocity (x,z,y):", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Boost:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Rotation 1:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Rotation 2:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Rotation 3:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Rotation 4:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Rotation 5:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Rotation 6:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Rotation 7:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Rotation 8:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Rotation 9:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(blueLabelFrame, text="Ball pos (x,z,y):", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()

		Label(orngLabelFrame, text="Position (x,z,y):", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Velocity (x,z,y):", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Boost:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Rotation 1:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Rotation 2:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Rotation 3:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Rotation 4:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Rotation 5:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Rotation 6:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Rotation 7:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Rotation 8:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Rotation 9:", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()
		Label(orngLabelFrame, text="Ball vel (x,z,y):", justify="left", anchor="w", width=self.PLAYER_LABEL_WIDTH).pack()

		# Create value for labels
		Label(blueValueFrame, textvariable=self.blueXZYPos, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueXZYVel, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueBoost, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueRot1, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueRot2, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueRot3, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueRot4, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueRot5, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueRot6, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueRot7, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueRot8, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.blueRot9, fg="blue", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(blueValueFrame, textvariable=self.ballXZYPos, fg="purple4", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		
		Label(orngValueFrame, textvariable=self.orngXZYPos, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngXZYVel, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngBoost, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngRot1, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngRot2, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngRot3, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngRot4, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngRot5, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngRot6, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngRot7, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngRot8, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.orngRot9, fg="darkorange2", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()
		Label(orngValueFrame, textvariable=self.ballXZYVel, fg="purple4", justify="left", anchor="w", width=self.PLAYER_VALUE_WIDTH).pack()

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

		# CONTROLLER PRESS FRAME
		Label(blueControllerLabel, text="P1:", justify="left", anchor="w", width=self.SCOREBOARD_SCORE_WIDTH).pack()
		Label(orngControllerLabel, text="P2:", justify="left", anchor="w", width=self.SCOREBOARD_SCORE_WIDTH).pack()

		Label(blueControllerValue, textvariable=self.blueOutput, fg="blue", justify="left", anchor="w", width=self.OUTPUT_WIDTH).pack()
		Label(orngControllerValue, textvariable=self.orngOutput, fg="darkorange2", justify="left", anchor="w", width=self.OUTPUT_WIDTH).pack()

		# Display
		self.root.update_idletasks()
		self.root.update()
		
	def sanity_check_x(self, x):
		return ((x >= 0) and (x < self.FIELD_HEIGHT)) # need to run these for 2d map display so not plotting random illegal points after goal scored / demo
		
	def sanity_check_z(self, z):
		return ((z >= 0) and (z < self.FIELD_WIDTH))

	# FUNCTION TO UPDATE
	def UpdateDisplay(self, values):
		
		# First update all string values
		self.blueScore.set(int(values[1][0]))
		self.orngScore.set(int(values[1][1]))
		self.blueXZYPos.set(str(round(values[0][5],2)) + "," + str(round(values[0][1],2)) + "," + str(round(values[0][4],2)))
		self.orngXZYPos.set(str(round(values[0][18],2)) + "," + str(round(values[0][3],2)) + "," + str(round(values[0][17],2)))
		self.ballXZYPos.set(str(round(values[0][7],2)) + "," + str(round(values[0][2],2)) + "," + str(round(values[0][6],2)))
		self.blueXZYVel.set(str(round(values[0][28],2)) + "," + str(round(values[0][30],2)) + "," + str(round(values[0][29],2)))
		self.orngXZYVel.set(str(round(values[0][34],2)) + "," + str(round(values[0][36],2)) + "," + str(round(values[0][35],2)))
		self.ballXZYVel.set(str(round(values[0][31],2)) + "," + str(round(values[0][33],2)) + "," + str(round(values[0][32],2)))
		self.blueBoost.set(int(values[0][0]))
		self.orngBoost.set(int(values[0][37]))
		self.blueRot1.set(round(values[0][8],2))
		self.blueRot2.set(round(values[0][9],2))
		self.blueRot3.set(round(values[0][10],2))
		self.blueRot4.set(round(values[0][11],2))
		self.blueRot5.set(round(values[0][12],2))
		self.blueRot6.set(round(values[0][13],2))
		self.blueRot7.set(round(values[0][14],2))
		self.blueRot8.set(round(values[0][15],2))
		self.blueRot9.set(round(values[0][16],2))
		self.orngRot1.set(round(values[0][19],2))
		self.orngRot2.set(round(values[0][20],2))
		self.orngRot3.set(round(values[0][21],2))
		self.orngRot4.set(round(values[0][22],2))
		self.orngRot5.set(round(values[0][23],2))
		self.orngRot6.set(round(values[0][24],2))
		self.orngRot7.set(round(values[0][25],2))
		self.orngRot8.set(round(values[0][26],2))
		self.orngRot9.set(round(values[0][27],2))
		self.orngDemos.set(int(values[1][2])) # Demos by orng, not when orng gets demo!
		self.blueDemos.set(int(values[1][3]))
		self.bluePoints.set(int(values[1][4]))
		self.orngPoints.set(int(values[1][5]))
		self.blueGoals.set(int(values[1][6]))
		self.blueSaves.set(int(values[1][7]))
		self.blueShots.set(int(values[1][8]))
		self.orngGoals.set(int(values[1][9]))
		self.orngSaves.set(int(values[1][10]))
		self.orngShots.set(int(values[1][11]))
		
		# Draw blue player
		if (self.sanity_check_x(self.lastBlueX) and self.sanity_check_z(self.lastBlueZ)):
			for i in range(self.lastBlueZ, self.lastBlueZ + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastBlueX, self.lastBlueX + self.PLAYER_PIXEL_SIZE):
					self.field.put("lightgreen", (i, j))
		self.lastBlueX = int( (-1) * values[0][5] + (self.FIELD_HEIGHT / 2))
		self.lastBlueZ = int(values[0][1] + (self.FIELD_WIDTH / 2))
		if (self.sanity_check_x(self.lastBlueX) and self.sanity_check_z(self.lastBlueZ)):
			for i in range(self.lastBlueZ, self.lastBlueZ + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastBlueX, self.lastBlueX + self.PLAYER_PIXEL_SIZE):
					self.field.put("blue", (i, j))
				
		# Draw orange player
		if (self.sanity_check_x(self.lastOrngX) and self.sanity_check_z(self.lastOrngZ)):
			for i in range(self.lastOrngZ, self.lastOrngZ + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastOrngX, self.lastOrngX + self.PLAYER_PIXEL_SIZE):
					self.field.put("lightgreen", (i, j))
		self.lastOrngX = int( (-1) * values[0][18] + (self.FIELD_HEIGHT / 2))
		self.lastOrngZ = int(values[0][3] + (self.FIELD_WIDTH / 2))
		if (self.sanity_check_x(self.lastOrngX) and self.sanity_check_z(self.lastOrngZ)):
			for i in range(self.lastOrngZ, self.lastOrngZ + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastOrngX, self.lastOrngX + self.PLAYER_PIXEL_SIZE):
					self.field.put("darkorange2", (i, j))
				
		# Draw ball
		if (self.sanity_check_x(self.lastBallX) and self.sanity_check_z(self.lastBallZ)):
			for i in range(self.lastBallZ, self.lastBallZ + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastBallX, self.lastBallX + self.PLAYER_PIXEL_SIZE):
					self.field.put("lightgreen", (i, j))
		self.lastBallX = int( (-1) * values[0][7] + (self.FIELD_HEIGHT / 2))
		self.lastBallZ = int(values[0][2] + (self.FIELD_WIDTH / 2))
		if (self.sanity_check_x(self.lastBallX) and self.sanity_check_z(self.lastBallZ)):
			for i in range(self.lastBallZ, self.lastBallZ + self.PLAYER_PIXEL_SIZE):
				for j in range(self.lastBallX, self.lastBallX + self.PLAYER_PIXEL_SIZE):
					self.field.put("white", (i, j))
		
		# Now refresh gui
		self.root.update_idletasks()
		self.root.update()
		
	def UpdateKeyPresses(self, output1, output2):
		self.blueOutput.set(str(output1))
		self.orngOutput.set(str(output2))
		
		# Now refresh gui
		self.root.update_idletasks()
		self.root.update()
