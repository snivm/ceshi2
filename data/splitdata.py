import shutil
import os
from pathlib import Path
import random

train_size = 0.8

image_dir = Path('images')
label_dir = Path('labels')

image_train_dir = image_dir / 'train'
image_val_dir = image_dir / 'val'

label_train_dir = label_dir / 'train'
label_val_dir = label_dir / 'val'

for p in [image_train_dir, image_val_dir, label_train_dir, label_val_dir]:
    p.mkdir(exist_ok=True)

# 先把数据都移到训练集里
for image in image_dir.glob('*.jpg'):
    shutil.move(image, image_train_dir / image.name)

# 先把数据都移到训练集里
for label in label_dir.glob('*.txt'):
    shutil.move(label, label_train_dir / label.name)

labels = list(label_train_dir.glob('*.txt'))
random.shuffle(labels)

len_train = int(len(labels) * train_size)
vals = labels[len_train:]

print('total', len(labels))
print('train', len_train)
print('val', len(labels) - len_train)

for vp in vals:
    shutil.move(vp, label_val_dir / vp.name)
    im_name = vp.stem + '.jpg'
    shutil.move(image_train_dir / im_name, image_val_dir / im_name)