# Importing Libraries 
import time 
import json
import pandas as pd
import numpy as np
import paho.mqtt.client as mqtt

# combo value
combo = [1, 3, 3, 7]

points = None

buffer0 = []
buffer1 = []
buffer2 = []
#counter = 0
print("start!")


combo_match = True
combo_index = 0

def mqtt_publisher():
    # 0. define callbacks - functions that run when events happen.
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print("Connection returned result: " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("ECEM119_knockbox_project")
        # The callback of the client when it disconnects.

    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print('Unexpected Disconnect')
        else:
            print('Expected Disconnect')
        # The default message callback.
        # (won't be used if only publishing, but can still exist)

    def on_message(client, userdata, message):
        # print('Received message: ', str(message.payload)[2:-1])
        data = ((str(message.payload)[2:-1]).split(';'))[:-1]
        count = 0
        for d in data:
          if count % 3 == 0:
            buffer0.append(int(d))
          if count % 3 == 1:
            buffer1.append(int(d))
          if count % 3 == 2:
            buffer2.append(int(d))
          count += 1
           

                
    # 1. create a client instance.
    client = mqtt.Client()
    # add additional client options (security, certifications, etc.)
    # many default options should be good to start off.
    # add callbacks to client.
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # 2. connect to a broker using one of the connect*() functions.
    # client.connect_async("test.mosquitto.org")
    client.connect_async('mqtt.eclipseprojects.io')

    # 3. call one of the loop*() functions to maintain network traffic flow with the broker.
    client.loop_start()
    # 4. use subscribe() to subscribe to a topic and receive messages.
    # 5. use publish() to publish messages to the broker.
    # payload must be a string, bytearray, int, float or None.
    #client.publish("ECEM119", curr, qos=1)


def knock_path(classification, index):
  if index < 10:
    return f"/Users/warren_wallis/Downloads/knock_data_v3/{classification}{index}.csv"
  else:
    return f"/Users/warren_wallis/Downloads/knock_data_v3_test/{classification}{index-10}.csv"
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

def main():
  mqtt_publisher()
  global points
  points = generate_points([i for i in range(0, 20)])
  while(True):
      global buffer1, buffer0, buffer2
      if (len(buffer1) >= 4):
          #print(counter)
          df = pd.DataFrame({'sensor0': buffer0, 'sensor1' : buffer1, 'sensor2' : buffer2})
          #df.to_csv(f"{counter}.csv")
          #print(df)
          # TODO: fill data
          knock_data = df
          guesses = calculate_k_nearest_neighbors(points, knock_data, k=15)
          print(guesses)
          global combo_index
          if combo[combo_index % 4] not in guesses:
              combo_match = False
          combo_index += 1

          if combo_index % 4 == 0:
            print(combo_match)
            combo_match = True

          
          buffer0 = []
          buffer1 = []
          buffer2 = []

if __name__ == '__main__':
  main()
