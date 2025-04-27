import math
from torch.nn import functional as F
import torch
from torch import nn
from torchvision import models, transforms
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

global model
model = None


def load_model():
    """加载YOLO模型"""
    global model
    if model is None:
        model_path = "./static/ai_model/best.pt"
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        device = 'cpu'  # 如果强制使用CPU，取消注释这行
        model = YOLO(model_path)
        model.to(device)
    return model


def resize_frame(frame, target_width=600):
    """调整帧大小，宽度固定为600"""
    height, width = frame.shape[:2]
    target_height = int(height * (target_width / width))
    return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)


def process_video(video_path, output_path="output_video.mp4", skip_frames=2):
    """
    处理视频的函数
    参数：
        video_path (str): 输入视频文件路径
        output_path (str): 输出视频文件路径
        skip_frames (int): 每隔几帧处理一次
    """
    # 加载模型
    load_model()

    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # 获取原始视频的FPS
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 设置输出视频的宽度
    target_width = 600

    # 创建视频写入对象（先用临时尺寸，后面会更新）
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None

    frame_count = 0
    last_result = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 调整帧大小
        frame = resize_frame(frame, target_width)

        # 初始化输出视频（在第一帧时）
        if out is None:
            frame_height = frame.shape[0]
            out = cv2.VideoWriter(output_path, fourcc, fps, (target_width, frame_height))

        # 每skip_frames帧处理一次
        if frame_count % skip_frames == 0:
            # 将OpenCV帧转换为RGB格式的PIL图像
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)

            # YOLO检测
            res = model.predict(pil_image)
            res = res[0]
            # 获取检测结果图像
            result_array = res.plot()
            # 转换为BGR格式以保存和显示
            frame_with_result = cv2.cvtColor(result_array, cv2.COLOR_RGB2BGR)
            frame_with_result = result_array
            last_result = frame_with_result
            print(f"Frame {frame_count}: Processed with YOLO detection")
        else:
            # 对于未处理的帧，使用上次的检测结果（如果有）或原始帧
            frame_with_result = last_result if last_result is not None else frame
            print(f"Frame {frame_count}: Using previous detection result")

        # 写入输出视频
        out.write(frame_with_result)

        # 显示帧
        cv2.imshow('Frame', frame_with_result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_count += 1

    # 释放资源
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video processing completed. Output saved to {output_path}")


if __name__ == "__main__":
    video_path = "vid/vid.mp4"
    process_video(video_path, skip_frames=2)