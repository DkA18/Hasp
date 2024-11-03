

class NeuralNetwork:
    def __init__(self, network: list):
        self.network = network
        self.error_rate = []
    
    def predict(self, input):
        output = input
        for layer in self.network:
            output = layer.forward(output)
            
        return output

    def train(self, loss, loss_prime, x_train, y_train, epochs = 1000, learning_rate = 0.01, verbose = True):
        for e in range(epochs):
            error = 0
            for x, y in zip(x_train, y_train):
                # forward
                output = self.predict(x)

                # error
                error += loss(y, output)

                # backward
                grad = loss_prime(y, output)
                for layer in reversed(self.network):
                    grad = layer.backward(grad, learning_rate)

            error /= len(x_train)
            self.error_rate.append(error)
            if verbose and (e + 1)%10 == 0:
                print(f"{e + 1}/{epochs}, error={error}")
