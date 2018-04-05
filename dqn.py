# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 11:22:54 2018

@author: Huy Pham
"""
import numpy as np
import tensorflow as tf
import cv2
from collection import deque
import random

tf.reset_default_graph()



ACTION = 3


### Build Graph



learning_rate = 1e-6

action = tf.place(tf.float32, [None, ACTION])
y = tf.place(tf.float32, [None])

input = tf.placeholder(tf.float32, [None,80,80,4])


layer2 = tf.layers.conv2d(layer1, channels = 16, kernel_size = (8,8), stride = 5, activation=tf.nn.relu)
## 5 x 7 x 16

flat_layer = tf.reshape(layer2, [-1, 5 * 7 *16 ])

hidden_layer = tf.layers.dense(flat_layer, units = 128, activation=tf.nn.relu)
## 128 x 1 connected layer

output_layer = tf.layers.dense(hidden_layer, units =  ACTION)

#action = tf.arg_max(output_layer,axis = 0)

readout_action = tf.tensordot(output_layer, action, axis = 1)

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

with tf.Session() as sess:    
    init = tf.global_variables_initializer()
    sess.run(init)
    epsilon = 1
    
    t=0
    while 1:
        actions_dist = sess.run(output_layer, feeddict = {input: state0}) #[0]
        actions = np.zeros(ACTION)
        if np.random.rand() <= epsilon or t <= 500:
            action_index = np.random.choice(actions)
        else:
            action_index = np.argmax(actions_dist)
        actions[action_index] = 1
        
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
            actions_dist1 = sess.run(output_layer, feeddict = {input: states1_batch})
            for i in range(len(minibatch)):
                if minibacth[i][4]:
                    targets.append(reward_batch[i])
                else:
                    targets.append(reward_batch[i] + 0.99 * np.max(actions_dist1[i]))
            
            sess.run(train_ops, dictfeed = {y:targets, input: state0_batch, action: actions_batch})
        
        #update frames
        screen0 = screen1
        t += 1
        
         # save progress every 10000 iterations
        if t % 10000 == 0:
            saver.save(sess, 'saved_networks/' + GAME + '-dqn', global_step = t)
        
            
            


    
