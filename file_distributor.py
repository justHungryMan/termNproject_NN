import os
import glob
import shutil
import random


data_dir = os.getcwd() + '/data'

train_dir = os.getcwd() + '/train'
train_count = 0

if not os.path.isdir(train_dir):
    os.mkdir(train_dir)

test_dir = os.getcwd() + '/test'
test_count = 0
if not os.path.isdir(test_dir):
    os.mkdir(test_dir)

portion = 0.2

with open('animal.txt', 'r') as file:
    line = None

    while line != '':
        line = file.readline()

        class_name = line.strip('\n')
        class_dir = data_dir + '/' + class_name
        class_images = glob.glob(class_dir + '/*.jpg')
        for file_path in class_images:
            p = random.random()
            print(file_path)
            if p < portion:
                shutil.copy(file_path, test_dir + '/' + "%05d.jpg"%test_count)
                test_count += 1
            else:
                shutil.copy(file_path, train_dir + '/' + "%05d.jpg"%train_count)
                train_count += 1
file.close()


