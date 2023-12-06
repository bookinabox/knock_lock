# Importing Libraries 
import serial 
import time 
import json
import pandas as pd
import numpy as np


def knock_path(classification, index):
  if index < 10:
    return f"C:/Users/powde/knock_receiver/knock_data_v3/{classification}{index}.csv"
  else:
    return f"C:/Users/powde/knock_receiver/knock_data_v3_test/{classification}{index-10}.csv"
def get_data(classification, index):
  return pd.read_csv(knock_path(classification, index), usecols=['sensor0', 'sensor1', 'sensor2'])
def get_test_data(classification, index):
  return pd.read_csv(knock_path(f"knock_data_v3_test/{classification}", index), usecols=['sensor0', 'sensor1', 'sensor2'])


def calculate_point(data):
  delays = data.idxmax()
  return delays
#   rel_delays = delays - delays.min()
#   return rel_delays

def generate_points(indicies):
  points = []
  for i in range(9):
    aggr = []
    for j in indicies:
      data = get_data(i, j)
      point = calculate_point(data)
      aggr.append(point)
    points.extend(aggr)
    aggr = np.array(aggr)
    # print(i, aggr.mean(axis=0), aggr.std(axis=0))
    # points.append(aggr.mean(axis=0))
  return np.array(points)

def calculate_guess(points, data):
  delays = data.idxmax()
  rel_delays = delays - delays.min()
  p1 = rel_delays.dot(points)
  dist = points - [rel_delays]
  dist = dist * dist
  dist = dist.sum(axis = 1)
  guess = dist.argmin()
  return guess

def calculate_k_nearest_neighbors(points, data, k):
  delays = data.idxmax()
  rel_delays = delays - delays.min()
  print(delays, rel_delays)
  dist = np.dot(points, rel_delays)
  dist = dist / (np.linalg.norm(points, axis=1) * np.linalg.norm(rel_delays))
#   dist = dist.sum(axis = 1)
  guess = dist.argpartition(k)[:k] / (len(points)/9)
  guess = guess.astype(int)
  return guess

def generate_guesses(points, indicies):
  guesses = []
  correct = 0
  for i in range(9):
    for j in indicies:
      data = get_data(i, j)
      delays = data.idxmax()
      rel_delays = delays - delays.min()
      dist = points - [rel_delays]
      dist = dist * dist
      dist = dist.sum(axis = 1)
      guess = dist.argmin()
      guesses.append(guess)
      if guess == i:
        correct += 1
  return (np.array(guesses), correct, 9 * len(indicies))

def k_nearest_neighbors(points, test, k):
  guesses = []
  correct = 0
  for i in range(9):
    for j in test:
      data = get_test_data(i, j)
      delays = data.idxmax()
    #   rel_delays = delays - delays.min()
      dist = points - [delays]
      dist = dist * dist
      dist = dist.sum(axis = 1)
      guess = dist.argpartition(k)[:k] / 10
      guess = guess.astype(int)
      values, counts = np.unique(guess, return_counts=True)
      guess = values[counts.argmax()]
      guesses.append(guess)
      if guess == i:
        correct += 1
  return (np.array(guesses), correct, 9 * len(test))

# combo value
combo = [1, 3, 3, 7]

points = generate_points([i for i in range(0, 20)])


arduino = serial.Serial(port='COM3', baudrate=38400, timeout=.1) 

buffer0 = []
buffer1 = []
buffer2 = []
#counter = 0
print("start!")


combo_match = True
combo_index = 0

while(True):
    c = arduino.readline()
    if c != b'':
        val = json.loads(c)
        buffer0.append(val[0])
        buffer1.append(val[1])
        buffer2.append(val[2])

    if (len(buffer1) >= 1024):
        #print(counter)
        df = pd.DataFrame({'sensor0': buffer0, 'sensor1' : buffer1, 'sensor2' : buffer2})
        #df.to_csv(f"{counter}.csv")
        #print(df)
        # TODO: fill data
        knock_data = df
        guesses = calculate_k_nearest_neighbors(points, knock_data, k=15)
        print(guesses)
        if combo[combo_index % 4] not in guesses:
            combo_match = False
        combo_index += 1

        if combo_index % 4 == 0:
          print(combo_match)
          combo_match = True

        #ounter += 1
        buffer0 = []
        buffer1 = []
        buffer2 = []

        
