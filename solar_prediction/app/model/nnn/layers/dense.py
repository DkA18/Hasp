import numpy as np
from .layer import Layer
from ..optimizers.adam import AdamOptimizer
from scipy import signal

class Dense(Layer):
    def __init__(self, input_size, output_size):
        self.weights = np.random.rand(output_size, input_size)
        self.bias = np.random.rand(output_size, 1)

    def forward(self, input):
        self.input = input
        return np.dot(self.weights, self.input) + self.bias

    def backward(self, output_gradient, learning_rate):
        weights_gradient = np.dot(output_gradient, self.input.T)
        input_gradient = np.dot(self.weights.T, output_gradient)
        self.weights -= learning_rate * weights_gradient
        self.bias -= learning_rate * output_gradient
        return input_gradient
        
class AdamDense(Layer):
    def __init__(self, input_size, output_size):
        self.weights = np.random.randn(output_size, input_size)
        self.bias = np.random.randn(output_size, 1)
        
        # Adam parameters
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.epsilon = 1e-8
        self.m_w, self.v_w = 0, 0  # Moments for weights
        self.m_b, self.v_b = 0, 0  # Moments for biases
        self.t = 0  # Time step for bias correction
        
    def forward(self, input):
        self.input = input
        return np.dot(self.weights, self.input) + self.bias


    def backward(self, output_gradient, learning_rate):
        weights_gradient = np.dot(output_gradient, self.input.T)
        input_gradient = np.dot(self.weights.T, output_gradient)
        
        # Update moments for Adam
        self.t += 1
        self.m_w = self.beta1 * self.m_w + (1 - self.beta1) * weights_gradient
        self.v_w = self.beta2 * self.v_w + (1 - self.beta2) * (weights_gradient ** 2)
        self.m_b = self.beta1 * self.m_b + (1 - self.beta1) * output_gradient
        self.v_b = self.beta2 * self.v_b + (1 - self.beta2) * (output_gradient ** 2)

        # Bias-corrected moments
        m_w_hat = self.m_w / (1 - self.beta1 ** self.t)
        v_w_hat = self.v_w / (1 - self.beta2 ** self.t)
        m_b_hat = self.m_b / (1 - self.beta1 ** self.t)
        v_b_hat = self.v_b / (1 - self.beta2 ** self.t)

        # Update weights and biases
        self.weights -= learning_rate * m_w_hat / (np.sqrt(v_w_hat) + self.epsilon)
        self.bias -= learning_rate * m_b_hat / (np.sqrt(v_b_hat) + self.epsilon)

        return input_gradient
    
class Convolutional(Layer):
    def __init__(self, input_shape, kernel_size, depth):
        input_depth, input_height, input_width = input_shape
        self.depth = depth
        self.input_shape = input_shape
        self.input_depth = input_depth
        self.output_shape = (depth, input_height - kernel_size + 1, input_width - kernel_size + 1)
        self.kernels_shape = (depth, input_depth, kernel_size, kernel_size)
        self.kernels = np.random.randn(*self.kernels_shape)
        self.biases = np.random.randn(*self.output_shape)

    def forward(self, input):
        self.input = input
        self.output = np.copy(self.biases)
        for i in range(self.depth):
            for j in range(self.input_depth):
                self.output[i] += signal.correlate2d(self.input[j], self.kernels[i, j], "valid")
        return self.output

    def backward(self, output_gradient, learning_rate):
        kernels_gradient = np.zeros(self.kernels_shape)
        input_gradient = np.zeros(self.input_shape)

        for i in range(self.depth):
            for j in range(self.input_depth):
                kernels_gradient[i, j] = signal.correlate2d(self.input[j], output_gradient[i], "valid")
                input_gradient[j] += signal.convolve2d(output_gradient[i], self.kernels[i, j], "full")

        self.kernels -= learning_rate * kernels_gradient
        self.biases -= learning_rate * output_gradient
        return input_gradient