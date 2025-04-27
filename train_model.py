import os
 
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ultralytics import YOLO 

# 代码要在 main 函数下运行 否则会报错 
if __name__ == '__main__':

    yolo = YOLO('yolov8s.yaml').load('yolov8s.pt')
    # yolo = YOLO('yolov8n.yaml')

    # 训练yolo模型 根据自己电脑GPU条件 修改batch即可
    yolo.train(data='data.yaml',  epochs=4, batch=8, workers=0)