import numpy as np
from .layer import Layer


class Dense(Layer):
    def __init__(self, input_size, output_size):
        self.weights = np.random.uniform(-1, 1,(output_size, input_size))
        self.bias = np.random.uniform(-1, 1,(output_size, 1)) 
        self.shape = [input_size, output_size]
        
    def __repr__(self):
        return f"Dense{self.shape}"
        
    def json_dict(self):
        return {"Dense": {"weights": self.weights.tolist(), "bias": self.bias.tolist(), "shape": self.shape}}

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
        self.weights = np.random.uniform(-1, 1,(output_size, input_size))
        self.bias = np.random.uniform(-1, 1,(output_size, 1)) 
        
        # Adam parameters
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.epsilon = 1e-8
        self.m_w, self.v_w = 0, 0  # Moments for weights
        self.m_b, self.v_b = 0, 0  # Moments for biases
        self.t = 0  # Time step for bias correction
        self.shape = [input_size, output_size]
        
    def forward(self, input):
        self.input = input
        return np.dot(self.weights, self.input) + self.bias

    def __repr__(self):
        return f"AdamDense{self.shape}"
        
    def json_dict(self):
        return {"AdamDense": {"weights": self.weights.tolist(), "bias": self.bias.tolist(), "shape": self.shape}}

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
    