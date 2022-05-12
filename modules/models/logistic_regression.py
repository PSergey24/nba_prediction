import os
import torch
import pandas as pd
import numpy as np
import torch.nn as nn
import torch.utils.data as Data
import torch.nn.functional as F
from torch.autograd import Variable


class LogisticRegression(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = torch.sigmoid(self.linear2(x))
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class Trainer:

    def __init__(self):
        self.lr = 0.001
        self.n_epoch = 40
        self.model = LogisticRegression(21, 264, 1)
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=self.lr)
        self.criterion = torch.nn.BCELoss(reduction='mean')

    def train(self):
        data = pd.read_csv('data/training_data/dataset_03.csv')
        data, test_data = self.get_data(data, 0.99)
        train_data, validation_data = self.get_data(data, 0.85)

        for epoch in range(self.n_epoch):
            x_data, y_data = self.df_to_tensor(train_data)
            train = Data.TensorDataset(x_data, y_data)

            train_loader = Data.DataLoader(train, batch_size=40, shuffle=True)
            for step, (batch_x, batch_y) in enumerate(train_loader):
                self.model.train()
                self.optimizer.zero_grad()

                x, y = Variable(batch_x), Variable(batch_y)

                y_predicted = self.model(x)
                loss = self.criterion(y_predicted, y)
                loss.backward()
                self.optimizer.step()

                if step % 100 == 0:
                    print(f'epoch: {epoch}-{step}, loss: {loss.item():.4f}')
        # self.model.save()

        with torch.no_grad():
            x_test, y_test = self.df_to_tensor(validation_data)

            y_predicted = self.model(x_test)
            y_predicted_cls = y_predicted.round()
            acc = y_predicted_cls.eq(y_test).sum() / float(y_test.shape[0])
            print(f'accuracy: {acc.item():.4f}')

            info_test, x_test, y_test = self.get_test_data(test_data)
            y_predicted = self.model(x_test)
            for i, item in enumerate(y_predicted):
                y_predicted_cls = item.round()
                if y_predicted_cls == 1:
                    print(f'winner is {info_test[i][0]}; probability: {item.detach().numpy()[0]}; result: {info_test[i][1]}; link: {info_test[i][3]}')
                else:
                    print(f'winner is {info_test[i][2]}; probability: {1 - item.detach().numpy()[0]}; result: {info_test[i][1]}; link: {info_test[i][3]}')

    @staticmethod
    def get_data(data, percent):
        data = data.sample(frac=1)
        train = data[:int(len(data) * percent)]
        test = data[int(len(data) * percent):]
        return train, test

    def df_to_tensor(self, data):
        x, y = self.shuffle_train(data)
        x = x.astype(np.float32)
        y = y.astype(np.float32)
        return torch.tensor(x.values), torch.tensor(y.values)

    @staticmethod
    def shuffle_train(data):
        data = data.sample(frac=1)
        X = data.loc[:, 'team_1':'home']
        Y = data.loc[:, 'Y':]
        return X, Y

    @staticmethod
    def get_test_data(data):
        info = data.loc[:, 'name_1':'link']
        x = data.loc[:, 'team_1':'home'].astype(np.float32)
        y = data.loc[:, 'Y':].astype(np.float32)
        return info.values, torch.tensor(x.values), torch.tensor(y.values)
