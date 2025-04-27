import math
from torch.nn import functional as F
import torch
from torch import nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from ultralytics import YOLO
import cv2
import torch
from torch import nn
from torchvision.models import alexnet, googlenet, vgg19
from torchvision.transforms import transforms
from ultralytics import YOLO
import tkinter as tk
import numpy as np
from ultralytics.utils.plotting import Annotator, colors

global model
model=None

global g_res
g_res=None
def process_image(image_path):
    """
    使用模型处理图像的函数。
    参数：
        image_path (str): 输入图像的文件路径。

    返回：
        PIL.Image: 显示在界面上的图像。
    """
    #model_path = "./static/ai_model/best_model.pt"
    model_path = "./static/ai_model/best.pt"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = 'cpu'
    global model
    if model is None:
        model = YOLO(model_path)
        model.to(device)
    image = Image.open(image_path).convert('RGB')
    res = model.predict(image)
    res = res[0]
    im0 = res.plot()
    result_image = Image.fromarray(im0[..., ::-1])

    global g_res
    g_res=res
    ####################
    # 获取类别名称列表
    names = res.names
    # 获取检测到的目标的类别索引
    cls = res.boxes.cls.cpu().numpy()
    # 获取检测到的目标的置信度
    conf = res.boxes.conf.cpu().numpy()
    # 遍历每个检测结果
    for i in range(len(cls)):
        class_index = int(cls[i])
        class_name = names[class_index]
        confidence = conf[i]
        print(f"检测到类别: {class_name}, 置信度: {confidence:.2f}")


    

    return result_image