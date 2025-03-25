
import numpy as np
from ..layers.layer import Layer

class Activation(Layer):
    def __init__(self, activation, activation_prime):
        self.activation = activation
        self.activation_prime = activation_prime
        
    def __repr__(self):
        return self.__class__.__name__
        
    def json_dict(self):
        return {self.__class__.__name__: ""}

    def forward(self, input):
        
        self.input = input
        return self.activation(self.input)

    def backward(self, output_gradient, learning_rate):
        return np.multiply(output_gradient, self.activation_prime(self.input))
    
class Linear(Activation):
    def __init__(self):
        def linear(x):
            return x

        def linear_prime(x):
            return np.ones_like(x)

        super().__init__(linear, linear_prime)

class Sigmoid(Activation):
    def __init__(self):
        def sigmoid(x):
            return 1 / (1 + np.exp(-x))

        def sigmoid_prime(x):
            return 1 / (1 + np.exp(-x)) * (1 - 1 / (1 + np.exp(-x)))

        super().__init__(sigmoid, sigmoid_prime)
        
class Swish(Activation):
    def __init__(self):
        def sigmoid(x):
            return 1 / (1 + np.exp(-x))
        
        def swish(x):
            return x * sigmoid(x)

        def swish_prime(x):
            s = sigmoid(x)
            return s*( 1 + x * ( 1 - s))

        super().__init__(swish, swish_prime)
        
class Tanh(Activation):
    def __init__(self):
        def tanh(x):
            return np.tanh(x)

        def tanh_prime(x):
            return 1 - np.tanh(x) ** 2

        super().__init__(tanh, tanh_prime)
        
class NormalizedTanh(Activation):
    def __init__(self):
        def tanh(x):
            return (np.tanh(x) + 1) /2

        def tanh_prime(x):
            return 0.5 * (1 - np.tanh(x)**2)

        super().__init__(tanh, tanh_prime)
        
class ReLU(Activation):
    def __init__(self):
        def relu(x):
            return np.maximum(0, x)
        def relu_prime(x):
            return np.where(x > 0, x, 0)
        super().__init__(relu, relu_prime)
        
class LReLU(Activation):
    def __init__(self):
        def lrelu(x):
            return np.maximum(0.1*x, x)
        def lrelu_prime(x):
            return np.where(x > 0, x, 0.1 * x)
        super().__init__(lrelu, lrelu_prime)
        
class Softplus(Activation):
    def __init__(self):
        def softplus(x):
            return np.log(1 + np.exp(x))

        def softplus_prime(x):
            return 1 / (1 + np.exp(-x))
        super().__init__(softplus, softplus_prime)
        