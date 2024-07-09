import torch
import torch.nn as nn

# make the model
class MoodRecognitionModel(nn.Module):
    def __init__(self, input_shape, hidden_units, dropout_rate):
        super().__init__()
        self.conv_block_1 = nn.Sequential(
            nn.Conv2d(in_channels=input_shape, # 1x48x48
                      out_channels=hidden_units,
                      kernel_size=3, # equivalent to tuple (3,3)
                      stride=1,
                      padding=1),
            nn.Dropout(dropout_rate),  # Adding dropout after max pooling
            nn.ReLU(),
            nn.Conv2d(in_channels=hidden_units,
                      out_channels=hidden_units,
                      kernel_size=3,
                      stride=1,
                      padding=1),
            nn.Dropout(dropout_rate),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # now becomes 24x24
        )
        self.conv_block_2 = nn.Sequential(
            nn.Conv2d(in_channels=hidden_units,
                      out_channels=hidden_units,
                      kernel_size=3,
                      stride=1,
                      padding=1),
            nn.Dropout(dropout_rate),  # Adding dropout after max pooling
            nn.ReLU(),
            nn.Conv2d(in_channels=hidden_units,
                      out_channels=hidden_units,
                      kernel_size=3,
                      stride=1,
                      padding=1),
            nn.Dropout(dropout_rate),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # now becomes 12x12
            nn.Dropout(dropout_rate),
        )
        self.conv_block_3 = nn.Sequential(
            nn.Conv2d(in_channels=hidden_units,
                      out_channels=hidden_units,
                      kernel_size=3,
                      stride=1,
                      padding=1),
            nn.Dropout(dropout_rate),  # Adding dropout after max pooling
            nn.ReLU(),
            nn.Conv2d(in_channels=hidden_units,
                      out_channels=hidden_units,
                      kernel_size=3,
                      stride=1,
                      padding=1),
            nn.Dropout(dropout_rate),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2), # now becomes 12x12
            nn.Dropout(dropout_rate),
        )

        # in each conv2d and maxPool layer the hidden_units get compressed
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_features=hidden_units*6*6, out_features=64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(in_features=64, out_features=6)
        )

    def forward(self,x):
        return self.classifier(self.conv_block_2(self.conv_block_3((self.conv_block_1(x)))))