# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 11:22:54 2018

@author: Huy Pham
"""
import numpy as np
import tensorflow as tf
import cv2
from collections import deque
import random

tf.reset_default_graph()


GAME = 'pong' # the name of the game being played for saved networks
ACTION = 3


### Build Graph



learning_rate = 1e-6

action = tf.placeholder(tf.float32, [None, ACTION])
y = tf.placeholder(tf.float32, [None])

inputs = tf.placeholder(tf.float32, [None,80,80,4])

initializer = tf.contrib.layers.variance_scaling_initializer()
conv0 = tf.contrib.layers.conv2d(inputs, 32, 8, 4, "SAME", weights_initializer=initializer, biases_initializer=initializer)
conv1 = tf.contrib.layers.conv2d(conv0, 64, 4, 2, "SAME", weights_initializer=initializer, biases_initializer=initializer)
conv2 = tf.contrib.layers.conv2d(conv1, 64, 3, 1, "SAME", weights_initializer=initializer, biases_initializer=initializer)
conv2 = tf.contrib.layers.flatten(conv2)
fc0 = tf.contrib.layers.fully_connected(conv2, 512, weights_initializer=initializer, biases_initializer=initializer)
outputs = tf.contrib.layers.fully_connected(fc0, ACTION, None, weights_initializer=initializer, biases_initializer=initializer)

readout_action = tf.tensordot(outputs, action, axes = 1)

loss = tf.reduce_mean(tf.square(y - readout_action))

train_ops = tf.train.AdamOptimizer(learning_rate).minimize(loss)


#### Training #####
import pong_fun as pf

game = pf.GameState()

#transition history
D = deque()
    
actions = np.zeros(ACTION)
actions[0] = 1
screen0, reward0, terminated = game.frame_step(actions)
screen0 = cv2.cvtColor(cv2.resize(screen0, (80, 80)), cv2.COLOR_BGR2GRAY)
ret, screen0 = cv2.threshold(screen0,1,255,cv2.THRESH_BINARY)
state0 = np.stack((screen0, screen0, screen0, screen0), axis = 2)

# saving and loading networks
saver = tf.train.Saver()

# printing
loss_file = open("logs_" + GAME + "/loss.txt", 'w')
    
with tf.Session() as sess:    
    init = tf.global_variables_initializer()
    sess.run(init)
    
    checkpoint = tf.train.get_checkpoint_state("saved_networks")
    if checkpoint and checkpoint.model_checkpoint_path:
        saver.restore(sess, checkpoint.model_checkpoint_path)
        print("Successfully loaded:", checkpoint.model_checkpoint_path)
    else:
        print ("Could not find old network weights")
    
    epsilon = 1
    
    t=0
    while 1:
        actions_dist = sess.run(outputs, feed_dict = {inputs: [state0]}) #[0]
        actions = np.zeros(ACTION)
        if np.random.rand() <= epsilon or t <= 500:
            action_index = np.random.choice(actions)
        else:
            action_index = np.argmax(actions_dist)
        actions[int(action_index)] = 1
        
        #decrease epsilon
        if epsilon > 0.05 and t > 500: 
            epsilon -= 0.95/500
            
        for i in range(1):
            #run the select action
            screen1, reward1, terminated = game.frame_step(actions)
            screen1 = cv2.cvtColor(cv2.resize(screen1, (80, 80)), cv2.COLOR_BGR2GRAY)
            ret, screen1 = cv2.threshold(screen1,1,255,cv2.THRESH_BINARY)
            state1 = np.stack((screen1, screen1, screen1, screen1), axis = 2)
            
            D.append((state0, actions, reward1, state1, terminated))
            if len(D) > 590000:
                D.popleft()
            
        #start training
        if t > 500:
            minibatch = random.sample(D,32)
            
            #get_batch variables
            state0_batch = [d[0] for d in minibatch]
            actions_batch = [d[1] for d in minibatch]
            reward_batch = [d[2] for d in minibatch]
            state1_batch = [d[3] for d in minibatch]

            targets = []
            actions_dist1 = sess.run(outputs, feed_dict = {inputs: state1_batch})
            for i in range(len(minibatch)):
                if minibatch[i][4]:
                    targets.append(reward_batch[i])
                else:
                    targets.append(reward_batch[i] + 0.99 * np.max(actions_dist1[i]))
                
            loss_t = sess.run(loss, feed_dict = {y:targets, inputs: state0_batch, action: actions_batch})
            sess.run(train_ops, feed_dict = {y:targets, inputs: state0_batch, action: actions_batch})
            
            #writing loss to file
            loss_file.write(str(loss_t)+ '\n')
            
        #update frames
        screen0 = screen1
        t += 1
        
         # save progress every 10000 iterations
        if t % 10000 == 0:
            saver.save(sess, 'saved_networks/' + GAME + '-dqn', global_step = t)
            
            
        
            
            


    
