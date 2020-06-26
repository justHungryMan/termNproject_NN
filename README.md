# termNproject_NN
---
[2020_1학기] 신경회로망특론 :  220200019 이성준

## File & Directory
1. crawling.py : 크롤링 코드
2. coderunner.py : crawling.py 를 쉽게 실행하는 코드
3. fileDistributor.py : crawling 한 데이터를 일정 비율로 train/test dataset 으로 나눠줌 (default 0.2)
4. animal.txt : class
5. easy-faster-rcnn.pytorch : faster-rcnn code


## Download
1. Model : [Pre-trained model](https://www.dropbox.com/sh/zeck2ha1tj92w9u/AABsQB_FP5LT48yBtW3DyhuWa?dl=0)
2. Dataset : [Dataset](https://www.dropbox.com/s/vuq9q2yb56g9h22/VOCdevkit.tar?dl=0)
3. Test : [Result](https://www.dropbox.com/s/gowycz52z05a61s/test.tar?dl=0)


## Requirements
---
- Python 3.6
- torch 1.1 +
- torchvision 0.2.1 +
- tqdm

## Setup
---
1. [Dataset](https://www.dropbox.com/s/vuq9q2yb56g9h22/VOCdevkit.tar?dl=0)
2. Non Maximum Suppression and ROI Align modules
   ```
   $ python support/setup.py develop
   ```

## Usage
---
1. Train
    ```
    bash script/voc2007/jun.sh resnet101 /path/to/train/dataset/dir
    ```
2. Infer
   ```
   bash script/voc2007/infer.sh resnet101 /path/to/checkpoint.pth /path/to/test/dataset/dir /path/to/output/image/dir
   ```

## Class not in ImageNet
---
1. raccoon
2. fennec fox
3. Long-tailed tit
4. Rhinoceros
5. pangolin
6. seal
7. bat
8. dolphine
9. tuna
10. hawk
11. parrot
12. octopus
13. reindeer
14. alpaca
15. Sunfish
16. mosquito
17. Goat
18. Tarsier
19. margay
20. Cuscus