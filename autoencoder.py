"""
Autoencoder for Neural Network interpretability.

The autoencoder is based on the paper: "Towards Monosemanticity: Decomposing Language Models With Dictionary Learning."
"""
import torch
from torch import nn
from torch.nn import functional as F


class Autoencoder(nn.Module):

    def __init__(self, n_activations, n_features):
        super(Autoencoder, self).__init__()
        self.shared_b_d = nn.Parameter(torch.zeros(n_activations))  # pre-encoder bias (shared)
        self.encoder = _Encoder(n_activations, n_features, self.shared_b_d)
        self.decoder = _Decoder(n_activations, n_features, self.shared_b_d)

    def forward(self, x):
        features = self.encoder(x)
        x = self.decoder(features)

        return x, features


class _Encoder(nn.Module):

    def __init__(self, n_activations, n_features, shared_b_d):
        super(_Encoder, self).__init__()
        self.W_e = nn.Linear(n_activations, n_features, bias=False)  # activations to features projection
        self.b_d = shared_b_d  # pre-encoder bias
        self.b_e = nn.Parameter(torch.zeros(n_features))  # encoder bias

        self.register_parameter('b_d', self.b_d)
        self.register_parameter('b_e', self.b_e)

    def forward(self, x):
        x = x - self.b_d
        x = self.W_e(x)
        x = x + self.b_e
        return F.relu(x)


class _Decoder(nn.Module):

    def __init__(self, n_activations, n_features, shared_b_d):
        super(_Decoder, self).__init__()
        self.W_d = nn.Linear(n_features, n_activations, bias=False)  # features to activations projection
        self.b_d = shared_b_d

    def forward(self, x):
        x = self.W_d(x)
        return x + self.b_d
