import numpy as np

def mse(y_true, y_pred):
    return np.mean(np.power(y_true - y_pred, 2))

def mse_prime(y_true, y_pred):
    return 2 * (y_pred - y_true) / np.size(y_true)

def mae(y_true, y_pred):
    return np.mean(np.abs(y_pred - y_true))

def mae_prime(y_true, y_pred):
    return np.where(y_pred > y_true, 1, np.where(y_pred < y_true, -1, 0)) / len(y_true)

def binary_cross_entropy(y_true, y_pred):
    return np.mean(-y_true * np.log(y_pred) - (1 - y_true) * np.log(1 - y_pred))

def binary_cross_entropy_prime(y_true, y_pred):
    return ((1 - y_true) / (1 - y_pred) - y_true / y_pred) / np.size(y_true)


def cross_entropy_loss(y_true, y_pred):
    # Clip y_pred to prevent log(0)
    y_pred = np.clip(y_pred, 1e-12, 1 - 1e-12)
    loss = -np.sum(y_true * np.log(y_pred))
    return loss / y_true.shape[0]  # Return mean loss for the batch

def cross_entropy_prime(y_true, y_pred):
    # Clip y_pred to prevent division by zero
    y_pred = np.clip(y_pred, 1e-12, 1 - 1e-12)
    return -y_true / y_pred / y_true.shape[0]

def huber_loss(y_true, y_pred, delta=1.0):
    diff = y_true - y_pred
    is_small_error = np.abs(diff) <= delta
    squared_loss = 0.5 * diff**2
    linear_loss = delta * (np.abs(diff) - 0.5 * delta)
    return np.mean(np.where(is_small_error, squared_loss, linear_loss))

def huber_loss_prime(y_true, y_pred, delta=1.0):
    diff = y_true - y_pred
    is_small_error = np.abs(diff) <= delta
    return np.where(is_small_error, -diff, -delta * np.sign(diff))

def hinge_loss(y_true, y_pred):
    return np.mean(np.maximum(0, 1 - y_true * y_pred))

def hinge_loss_prime(y_true, y_pred):
    return np.where(y_true * y_pred < 1, -y_true, 0)

