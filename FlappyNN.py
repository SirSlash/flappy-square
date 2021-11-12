import tensorflow as tf
import FlappyEnv
import random
import numpy as np
import csv
from keras.models import Sequential
from keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt


path = "training_data_handmade.csv"
env = FlappyEnv.Env()

goal_steps = 10000
score_requirement = 3
intial_games = 50000
accepted_score = 10


ideal = None
env.reset()

rw = "r"

def model_data_preparation():
    games_count = 0
    training_data = []
    accepted_scores = []
    # for game_index in range(intial_games):
    while len(accepted_scores) < accepted_score:
        score = 0
        game_memory = []
        previous_observation = []
        # for step_index in range(goal_steps):
        while True:
            """Stellar"""
            # action = random.randrange(0, 2)

            """Flappi"""
            if random.randint(0, 100) > 98:
                action = 1
            else:
                action = 0
            # action = 0

            """Mario"""
            # if env.jumpable():
            #     if random.randint(0, 100) > 96:
            #         action = 1
            # if random.randint(0, 100) > 50:
            #     action = 1

            observation, reward, done, info = env.step(action)  # score in reward
            #env.render()
            if len(previous_observation) > 0:
                game_memory.append([previous_observation, action])
            previous_observation = observation
            score += reward
            if done:
                break

        if score >= score_requirement:
            accepted_scores.append(score)
            print(len(accepted_scores))
            for data in game_memory:
                # Origin
                # if data[1] == 1:
                #     output = [1, 0]
                # elif data[1] == 0:
                #     output = [0, 1]
                training_data.append([data[0], data[1]])
        games_count += 1
        if games_count % 1000 == 0:
            print(games_count)
        env.reset()

    print(accepted_scores)

    return training_data


def build_model(input_size):
    model = Sequential()
    model.add(Dense(4, input_dim=input_size, activation='relu'))
    model.add(Dense(2, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=Adam(), metrics=['accuracy'])

    return model

# Origin
# def train_model(training_data):
#     X = np.array([i[0] for i in training_data]).reshape(-1, len(training_data[0][0]))
#     y = np.array([i[1] for i in training_data]).reshape(-1, len(training_data[0][1]))
#     model = build_model(input_size=len(X[0]), output_size=len(y[0]))
#
#     model.fit(X, y, epochs=10)
#     return model
# Origin
# def build_model(input_size, output_size):
#     model = Sequential()
#     model.add(Dense(128, input_dim=input_size, activation='relu'))
#     model.add(Dense(52, activation='relu'))
#     model.add(Dense(output_size, activation='linear'))
#     model.compile(loss='mse', optimizer=Adam(), metrics=['accuracy'])
#
#     return


def train_model(training_data):
    X = np.array([i[0:4] for i in training_data])
    y = np.array([i[4] for i in training_data])
    model = build_model(input_size=len(X[0]))

    model.fit(X, y, epochs=10)
    return model


def csv_writer(data, path):
    data_line = []
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            for part in line[:1]:
                for element in part:
                    data_line.append(element)
            data_line.append(line[1])
            writer.writerow(data_line)
            data_line.clear()


def csv_reader(file_obj):
    data_array = np.loadtxt(file_obj, delimiter=',')
    return data_array


# Write to the file
# fl = model_data_preparation()
# csv_writer(fl, path)

# Read from the file
# trained_model = train_model(csv_reader(path))

# if rw == "w":
#     fl = model_data_preparation()
#     csv_writer(fl, path)
# elif rw == "r":
#     trained_model = train_model(csv_reader(path))
#
# trained_model.save('saved_model/flappy_model')
trained_model = tf.keras.models.load_model('saved_model/flappy_model')

#Working string
# trained_model = train_model(model_data_preparation())

# строим графики потерь и точности
# N = np.arange(0, 10)
# plt.style.use("ggplot")
# plt.figure()
# plt.plot(N, trained_model.history["loss"], label="train_loss")
# # plt.plot(N, trained_model.history["val_loss"], label="val_loss")
# plt.plot(N, trained_model.history["acc"], label="train_acc")
# # plt.plot(N, trained_model.history["val_acc"], label="val_acc")
# plt.title("Training Loss and Accuracy (Simple NN)")
# plt.xlabel("Epoch #")
# plt.ylabel("Loss/Accuracy")
# plt.legend()

scores = []
choices = []

for each_game in range(10):
    score = 0
    prev_obs = []
    # for step_index in range(goal_steps):
    while True:
        # env.render()
        if len(prev_obs) == 0:
            action = 0
        else:
            fl = trained_model.predict(prev_obs.reshape(-1, len(prev_obs)))[0]
            if fl < 0.2:
                action = 0
            else:
                action = 1
            # print(fl)

        choices.append(action)
        new_observation, reward, done, info = env.step(action)
        prev_obs = new_observation
        score += reward
        # print(score)
        if done:
            break

    env.reset()
    scores.append(score)

print(scores)
print('Average Score:', sum(scores) / len(scores))
print('choice 1:{}  choice 0:{}'.format(choices.count(1) / len(choices), choices.count(0) / len(choices)))
