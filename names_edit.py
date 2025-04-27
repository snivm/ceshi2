from ultralytics import YOLO

# 加载训练好的模型
model = YOLO('static/ai_model/best.pt')
 

# 定义新的类别名称
new_names = ['Bad', 'Good']

# 设置模型的类别名称
model.names = new_names

# 查看更新后的类别名称
print("Updated class names:", model.names)

'''
# 进行推理
results = model.predict(source='path/to/image.jpg')

# 打印推理结果，使用新的类别名称
for result in results:
    boxes = result.boxes
    for box in boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        print(f"Detected class: {class_name}")'
'''

# 保存修改后的模型
model.save('static/ai_model/best_model.pt')

# 加载修改后的模型
#updated_model = YOLO('path/to/updated_model.pt')
#print("Class names in updated model:", updated_model.names)