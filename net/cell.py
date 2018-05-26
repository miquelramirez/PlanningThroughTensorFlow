import tensorflow as tf
from keras.layers import Dropout, Dense, merge


class TrainedCell(tf.nn.rnn_cell.RNNCell):
    # Reward function is assumed to be hard defined

    def __init__(self, num_state_units, num_reward_units, num_hidden_units, num_hidden_layers, dropout, domain):
        self._num_state_units = num_state_units
        self._num_reward_units = num_reward_units
        self._num_hidden_units = num_hidden_units
        self._num_hidden_layers = num_hidden_layers
        self._dropout = dropout
        self._domain = domain

    @property
    def state_size(self):
        return self._num_state_units

    @property
    def output_size(self):
        return self._num_reward_units

    def __call__(self, inputs, state, scope=None):
        print(inputs.get_shape())
        with tf.variable_scope(scope):
            with tf.variable_scope("transition"):
                init = merge([inputs, state], mode='concat')
                x = Dense(self._num_hidden_units, activation='relu')(init)
                x = Dropout(self._dropout)(x)
                interm_inputs = merge([x, init], mode='concat')
                if self._num_hidden_layers > 1:
                    for i in range(self._num_hidden_layers-1):
                        x = Dense(self._num_hidden_units, activation='relu')(interm_inputs)
                        x = Dropout(self._dropout)(x)
                        interm_inputs = merge([x, interm_inputs], mode='concat')

                next_state = Dense(self._num_state_units, activation='linear')(interm_inputs)
            with tf.variable_scope("Reward"):
                reward = self._domain.Reward(state)
        return reward, next_state

    @staticmethod
    def load_trained(sess, path):
        generator_variables = []
        for v in tf.trainable_variables():
            if "transition" in v.name:
                generator_variables.append(v)
        saver = tf.train.Saver(generator_variables)
        saver.restore(sess, path)
