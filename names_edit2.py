from ultralytics import YOLO

# 加载已有的模型
model = YOLO('static/ai_model/best.pt')

# 设置训练参数并开始训练
results = model.train(
    data='data.yaml',
    epochs=1,
    lr0=0.001,
    batch=8
)
   # 训练yolo模型 根据自己电脑GPU条件 修改batch即可
    #yolo.train(data='data.yaml',  epochs=10, batch=8, workers=0)

# 保存训练后的模型
model.save('static/ai_model/best_model.pt')