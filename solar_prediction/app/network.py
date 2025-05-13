
from flask import current_app, redirect, url_for
from flask import app
from model.layers.dense import Dense, AdamDense
from model.activations.activation import *
from model.losses import *
import json
from copy import deepcopy
from models import ModelJSON, db
from numpy import float128, nan_to_num

class NeuralNetwork:
    def __init__(self, network: list = []):
        self.network = network
        self.error_rate = []
        self.real_error = []
        self.backup = None
    
    def predict(self, inp):
        output = inp
        for layer in self.network:
            output = layer.forward(output)
            
        return output
    
    def load(self, json_record):
        self.network = []
        self.error_rate = []
        self.real_error = []
        self.backup = None
        json_list: list = json.loads(json_record)
        for layer in json_list: 
            
            try:
                l = globals()[list(dict(layer).keys())[0]](*(list(dict(layer).values())[0]["shape"]))
                l.weights = np.asarray([np.asarray(json.loads(item), dtype=np.longdouble) for item in list(dict(layer).values())[0]["weights"]])
                l.bias = np.asarray([np.asarray(json.loads(item), dtype=np.longdouble) for item in list(dict(layer).values())[0]["bias"]])
            except (KeyError, TypeError):
                l = globals()[list(dict(layer).keys())[0]]()
            self.network.append(l) 

    
    def save(self):
        save_object = [n.json_dict() for n in self.network]

        return json.dumps(save_object)

    def train(self, loss, loss_prime, x_train, y_train, test_split=0.1, epochs = 1000, learning_rate = 0.01, verbose = True):
        split_idx = int(len(x_train) * (1 - test_split))
        x_train = np.array(x_train, dtype=np.longdouble)
        y_train = np.array(y_train, dtype=np.longdouble)
        x_test = x_train[split_idx:]
        y_test = y_train[split_idx:]
        x_train = x_train[:split_idx]
        y_train = y_train[:split_idx]
        
        tested = 0
        for e in range(epochs):
            error = 0
            for x, y in zip(x_train, y_train):
                output = self.predict(x)

                error += loss(y, output)
                # print(y,output, error)
                grad = loss_prime(y, output)
                for layer in reversed(self.network):
                    grad = layer.backward(grad, learning_rate)

            error /= len(x_train)
            self.error_rate.append(error)
            if verbose and (e + 1)%10 == 0:
                print(f"{e + 1}/{epochs}, error={error}")
            if (e + 1)%10 == 0:
                current = []
                valid_error = 0
                for x, y in zip(x_test, y_test):
                    p = self.predict(x)
                    pred = round(p.item() *10000)
                    actual = round(y.item()*10000)
                    valid_error += loss(y, p)
                    try:
                        percent  = round((pred/actual)*100)  
                    except:
                        percent  = 0 
                    current.append([pred, actual, percent])
                    if verbose:
                        print(f"Unit Validation epoch, actual={actual}, prediction={pred}, miss={np.abs(pred-actual).item()}, percentage={percent}%, y={y.item()}")
                tested += 1
                print(f"Complete Validation on {e + 1}/{epochs} epoch, actual={np.mean([actual[1] for actual in current]).round()}, prediction={np.mean([pred[0] for pred in current]).round()}, miss={np.mean([np.abs(l[0]-l[1]).item() for l in current]).round()}, percentage={np.mean([percent[2] for percent in current]).round()}%, valid_error={valid_error}, error={error}", flush=True)
                self.real_error.append(valid_error)
                
                if len(self.real_error) > 2:
                    if valid_error < self.real_error[-2]:
                        self.backup = [deepcopy(e) for e in self.network]
                if len(self.real_error) > 5:
                    if self.real_error[-5] < np.mean(self.real_error[-4:]) and self.real_error[-5] < self.real_error[-1]:
                        self.network = self.backup
                        break   
        return self.save()
                
