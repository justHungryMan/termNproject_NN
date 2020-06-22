import os

data_dir = os.getcwd() + '/data'
if not os.path.isdir(data_dir):
    os.mkdir(data_dir)

with open('animal.txt', 'r') as file: 
    line = None    # 변수 line을 None으로 초기화
    while line != '':
        line = file.readline()
        animal = line.strip('\n')
        dir = os.getcwd() + '/data/' + animal
        if not os.path.isdir(dir):
            os.mkdir(dir)

        os.system("python crawling.py -q {q} -o {o}".format(q=animal, o=dir))

file.close()