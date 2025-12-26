import numpy as np
import math
import random
import pickle


class NeuralNetwork():
    def __init__(self, input_nodes, hidden_nodes1, output_nodes):
        self.input_nodes = input_nodes
        self.hidden_nodes1 = hidden_nodes1
        self.output_nodes = output_nodes

        # Khởi tạo trọng số với Xavier initialization
        self.in_hidden1_weights = np.random.randn(self.hidden_nodes1, self.input_nodes) * np.sqrt(
            2.0 / self.input_nodes)
        self.hidden1_output_weights = np.random.randn(self.output_nodes, self.hidden_nodes1) * np.sqrt(
            2.0 / self.hidden_nodes1)
        self.in_hidden1_biases = np.zeros((self.hidden_nodes1, 1))
        self.hidden1_output_biases = np.zeros((self.output_nodes, 1))

        self.sigmoid_v = np.vectorize(self.sigmoid)

    def sigmoid(self, x):
        # Tránh overflow
        if x < -500:
            return 0
        elif x > 500:
            return 1
        return 1 / (1 + math.exp(-x))

    def feedforward(self, inputs):
        self.inputs = inputs

        # Hidden layer
        self.hidden_layer1 = self.in_hidden1_weights.dot(self.inputs)
        self.hidden_layer1 = self.sigmoid_v(self.hidden_layer1 + self.in_hidden1_biases)

        # Output layer
        self.output = self.hidden1_output_weights.dot(self.hidden_layer1)
        self.output = self.sigmoid_v(self.output + self.hidden1_output_biases)

        return self.output

    def crossover(self, mat1, mat2):
        """Lai ghép giữa 2 ma trận"""
        childMat = np.zeros((mat1.shape[0], mat1.shape[1]))
        x = mat1.shape[0] // 2
        childMat[:x], childMat[x:] = mat1[:x], mat2[x:]
        return childMat

    def mutate(self, mat, rate):
        """Đột biến ma trận với tỷ lệ nhất định"""
        for i in range(mat.shape[0]):
            if rate > random.uniform(0, 1):
                for j in range(mat.shape[1]):
                    mat[i][j] += np.random.randn() * 0.5  # Đột biến nhỏ hơn

    def serialize(self):
        """Lưu mạng neural thành bytes"""
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        """Khôi phục mạng neural từ bytes"""
        return pickle.loads(data)