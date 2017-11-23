#!/usr/bin/env python

import socket
import time
import random
import GameTickPacket_pb2

TCP_IP = '127.0.0.1'
TCP_PORT = 35401
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

while 1:
    time.sleep(1)

    sample = GameTickPacket_pb2.GameTickPacket()

    sample.gameball.Location.x = 0
    sample.gameball.Location.y = 0
    sample.gameball.Location.z = random.uniform(0, 10)
    sample.gameball.Rotation.x = 0
    sample.gameball.Rotation.y = 0
    sample.gameball.Rotation.z = 0
    sample.gameball.Velocity.x = 0
    sample.gameball.Velocity.y = 0
    sample.gameball.Velocity.z = 0
    sample.gameball.AngularVelocity.x = 0
    sample.gameball.AngularVelocity.y = 0
    sample.gameball.AngularVelocity.z = 0
    sample.gameball.Acceleration.x = 0
    sample.gameball.Acceleration.y = 0
    sample.gameball.Acceleration.z = 0

    orangeCar = sample.gamecars.add()
    orangeCar.Location.x = 10
    orangeCar.Location.y = 90
    orangeCar.Location.z = 1
    orangeCar.Rotation.x = 0
    orangeCar.Rotation.y = 0
    orangeCar.Rotation.z = 0
    orangeCar.Score.Score = 250
    orangeCar.Score.Goals = 1
    orangeCar.Score.Assists = 0
    orangeCar.Score.Saves = 0
    orangeCar.Score.Shots = 1
    orangeCar.Score.Demolitions = 0
    orangeCar.SuperSonic = False
    orangeCar.Bot = False
    orangeCar.Team = "orange"
    orangeCar.Boost = 100

    blueCar = sample.gamecars.add()
    blueCar.Location.x = -10
    blueCar.Location.y = -90
    blueCar.Location.z = 1
    blueCar.Rotation.x = 0
    blueCar.Rotation.y = 0
    blueCar.Rotation.z = 0
    blueCar.Score.Score = 0
    blueCar.Score.Goals = 0
    blueCar.Score.Assists = 0
    blueCar.Score.Saves = 0
    blueCar.Score.Shots = 0
    blueCar.Score.Demolitions = 0
    blueCar.SuperSonic = False
    blueCar.Bot = False
    blueCar.Team = "blue"
    blueCar.Boost = 100

    s.send(sample.SerializeToString())
conn.close()