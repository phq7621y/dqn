# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 11:22:54 2018

@author: Huy Pham
"""
import numpy as np
import tensorflow as tf





### Build Graph






pixels = tf.placeholder((-1, 80,60, 1))



layer1 = tf.layers.conv2d(pixels, channels = 8, kernel_size = (6,6), stride = 2, activation=tf.nn.relu)
## 28 x 38 x 8 layer

layer2 = tf.layers.conv2d(layer1, channels = 16, kernel_size = (8,8), stride = 5, activation=tf.nn.relu)
## 5 x 7 x 16

flat_layer = tf.reshape(layer2, [-1, 5 * 7 *16 ])

hidden_layer = tf.layers.dense(flat_layer, units = 128, activation=tf.nn.relu)
## 128 x 1 connected layer

output_layer = tf.layers.dense(hidden_layer, units =  3)

action = tf.arg_max(output_layer,axis = 0)

loss = ??

optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)

train_op = optimizer.minimize(loss=loss)




#### Optimize
import pong_interface as pi
