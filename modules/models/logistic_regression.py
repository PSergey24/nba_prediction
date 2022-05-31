import os
import torch
import pandas as pd
import numpy as np
import torch.nn as nn
import torch.utils.data as Data
import torch.nn.functional as F
from torch.autograd import Variable
from datetime import date
from modules.db_worker import DBWorker


class LogisticRegression(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = torch.sigmoid(self.linear2(x))
        return x

    def save(self, way_to_model):
        folders = way_to_model.split('/')
        model_folder_path, file_name = '/'.join(folders[:-1]), folders[-1]
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class Trainer:

    def __init__(self):
        self.lr = 0.001
        self.n_epoch = 40
        self.batch_size = 40
        self.model = LogisticRegression(20, 264, 1)
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=self.lr)
        self.criterion = torch.nn.BCELoss(reduction='mean')
        self.way_to_model = f'data/models/model_lr_{date.today().day}_{date.today().month}_{date.today().year}/model.pth'
        self.way_to_dataset = None
        self.accuracy = None
        self.db_worker = DBWorker('data/db/nba.db')

    def main(self):
        data = self.get_train_data()
        data = self.filter_nan_rows(data)
        self.train(data)
        self.save_model()

    def get_train_data(self):
        files = self.get_list_files('data/training_data/')
        train_file = self.get_newest_file(files)
        self.way_to_dataset = f'data/training_data/{train_file}'
        data = pd.read_csv(self.way_to_dataset)
        return data

    @staticmethod
    def get_list_files(path):
        return [{'file': file, 'date': os.path.getmtime(path + file)} for file in os.listdir(path) if '.csv' in file]

    @staticmethod
    def get_newest_file(files):
        files = sorted(files, key=lambda d: d['date'], reverse=True)
        return files[0]['file']

    @staticmethod
    def filter_nan_rows(data):
        return data.dropna()

    def train(self, data):
        data, test_data = self.split_data(data, 0.99)
        train_data, validation_data = self.split_data(data, 0.85)

        for epoch in range(self.n_epoch):
            info_data, x_data, y_data = self.df_to_tensor(train_data)
            train = Data.TensorDataset(x_data, y_data)

            train_loader = Data.DataLoader(train, batch_size=self.batch_size, shuffle=True)
            for step, (batch_x, batch_y) in enumerate(train_loader):
                self.model.train()
                self.optimizer.zero_grad()

                x, y = Variable(batch_x), Variable(batch_y)

                y_predicted = self.model(x)
                loss = self.criterion(y_predicted, y)
                loss.backward()
                self.optimizer.step()

                # if step % 100 == 0:
                #     print(f'epoch: {epoch}-{step}, loss: {loss.item():.4f}')

        with torch.no_grad():
            info_test, x_test, y_test = self.df_to_tensor(validation_data)

            y_predicted = self.model(x_test)
            y_predicted_cls = y_predicted.round()
            acc = y_predicted_cls.eq(y_test).sum() / float(y_test.shape[0])
            self.accuracy = acc.item()

            # self.to_test(test_data)

    def split_data(self, data, percent):
        data = self.shuffle_data(data)
        train = data[:int(len(data) * percent)]
        test = data[int(len(data) * percent):]
        return train, test

    @staticmethod
    def shuffle_data(data):
        return data.sample(frac=1)

    def df_to_tensor(self, data):
        data = self.shuffle_data(data)
        info, x, y = self.split_to_group(data)
        x = x.astype(np.float32)
        y = y.astype(np.float32)
        return info.values, torch.tensor(x.values), torch.tensor(y.values)

    @staticmethod
    def split_to_group(data):
        info = data.loc[:, 'link':'id_home']
        X = data.loc[:, 'ELO_visitor':'home_b2b']
        Y = data.loc[:, 'Y':]
        return info, X, Y

    def to_test(self, test_data):
        info_test, x_test, y_test = self.df_to_tensor(test_data)
        y_predicted = self.model(x_test)
        for i, item in enumerate(y_predicted):
            y_predicted_cls = item.round()
            if y_predicted_cls == 1:
                print(
                    f'winner is {info_test[i][5]} (id_team) visitor_team; probability: {item.detach().numpy()[0]}; result: {info_test[i][3]}-{info_test[i][4]}; link: {info_test[i][0]}')
            else:
                print(
                    f'winner is {info_test[i][6]} (id_team) home_team; probability: {1 - item.detach().numpy()[0]}; result: {info_test[i][3]}-{info_test[i][4]}; link: {info_test[i][0]}')

    def save_model(self):
        models = self.db_worker.get_all('models')

        if len(models) == 0:
            self.model.save(self.way_to_model)
            self.save_model_info_to_db()
            print(f"This model's version has been saved")
            return

        is_better_model = self.compare_model(models)
        if is_better_model is True:
            self.model.save(self.way_to_model)
            self.save_model_info_to_db()
            print(f"New model is better; This model's version has been saved")
            return
        print(f"New model not better; This model's version has not been saved")

    def compare_model(self, models):
        models.sort(key=lambda x: x[2], reverse=True)
        if self.accuracy > models[0][2]:
            return True
        else:
            return False

    def save_model_info_to_db(self):
        self.db_worker.insert_new_model('logistic_regression', self.accuracy, self.way_to_model, self.way_to_dataset)
