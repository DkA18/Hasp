class Layer:
    def __init__(self):
        self.input = None
        self.output = None
        
    def json_dict(self):
        NotImplemented()
        

    def forward(self, input):
        NotImplemented()

    def backward(self, output_gradient, learning_rate):
        NotImplemented()