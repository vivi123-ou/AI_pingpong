import numpy as np
import math
import random
import pickle


class NeuralNetwork():
    """Mạng Neural Network cho AI Ping Pong"""

    def __init__(self, input_nodes, hidden_nodes1, output_nodes):
        self.input_nodes = input_nodes
        self.hidden_nodes1 = hidden_nodes1
        self.output_nodes = output_nodes

        # Khởi tạo trọng số với Xavier/He initialization
        self.in_hidden1_weights = np.random.randn(self.hidden_nodes1, self.input_nodes) * np.sqrt(
            2.0 / self.input_nodes)
        self.hidden1_output_weights = np.random.randn(self.output_nodes, self.hidden_nodes1) * np.sqrt(
            2.0 / self.hidden_nodes1)

        # Khởi tạo bias = 0
        self.in_hidden1_biases = np.zeros((self.hidden_nodes1, 1))
        self.hidden1_output_biases = np.zeros((self.output_nodes, 1))

        # Vectorize sigmoid function
        self.sigmoid_v = np.vectorize(self.sigmoid)

    def sigmoid(self, x):
        """Hàm sigmoid với xử lý overflow"""
        if x < -500:
            return 0.0
        elif x > 500:
            return 1.0
        return 1.0 / (1.0 + math.exp(-x))

    def feedforward(self, inputs):
        """Truyền thẳng qua mạng neural"""
        self.inputs = inputs

        # Layer 1: Input → Hidden
        self.hidden_layer1 = self.in_hidden1_weights.dot(self.inputs)
        self.hidden_layer1 = self.sigmoid_v(self.hidden_layer1 + self.in_hidden1_biases)

        # Layer 2: Hidden → Output
        self.output = self.hidden1_output_weights.dot(self.hidden_layer1)
        self.output = self.sigmoid_v(self.output + self.hidden1_output_biases)

        return self.output

    def crossover(self, mat1, mat2):
        """Lai ghép giữa 2 ma trận (từ 2 AI cha mẹ)"""
        childMat = np.zeros((mat1.shape[0], mat1.shape[1]))

        # Cắt ngang ở giữa
        x = mat1.shape[0] // 2
        childMat[:x] = mat1[:x]  # Nửa trên từ cha
        childMat[x:] = mat2[x:]  # Nửa dưới từ mẹ

        return childMat

    def mutate(self, mat, rate):
        """Đột biến ma trận với tỷ lệ nhất định"""
        for i in range(mat.shape[0]):
            # Mỗi hàng có xác suất 'rate' bị đột biến
            if rate > random.uniform(0, 1):
                for j in range(mat.shape[1]):
                    # Thêm nhiễu Gaussian nhỏ
                    mat[i][j] += np.random.randn() * 0.3

    def serialize(self):
        """Lưu toàn bộ mạng neural thành bytes"""
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        """Khôi phục mạng neural từ bytes"""
        return pickle.loads(data)