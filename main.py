import datetime
import os
from flask import Flask, jsonify, render_template, request, flash, redirect, url_for, session
import pymysql
from ai_model import process_image
import ai_model
from config import Config
 
app = Flask(__name__,static_folder='static')
app.template_folder = 'templates'
app.secret_key = 'lhf1990'  # 设置一个随机的、复杂的密钥
# 确保保存照片的文件夹存在
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 数据库连接配置
app.config['MYSQL_HOST'] = Config.MYSQL_HOST
app.config['MYSQL_USER'] = Config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = Config.MYSQL_DB

# 初始化数据库连接
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
# 初始化数据库连接
def get_db_connection2():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        charset='utf8mb4' 
    )
#注册页
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 检查用户名是否已存在
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                if user:
                    flash('账号已存在！')
                    return redirect(url_for('register'))
                
                # 插入新用户
                sql = "INSERT INTO users (username, password,usertype) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, password,'普通用户'))
            connection.commit()
            flash('注册成功！请登录。')
            return redirect(url_for('login'))
        finally:
            connection.close()
    #return render_template('register.html')
    return render_template('new_index.html')

#默认登录页
@app.route('/')
def login_page():
    #return render_template('login.html')
    return render_template('new_index.html')

#登录页
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 检查账号和密码
                sql = "SELECT * FROM users WHERE username = %s AND password = %s"
                cursor.execute(sql, (username, password))
                user = cursor.fetchone()
                if user:
                    #flash('登录成功！', 'success')
                    session["username"] = username 
                    session["usertype"] = user["usertype"]+""
                    #XZ-S
                    ip_address = request.remote_addr
                    record_login_log(username, ip_address)
                    #XZ-E
                    return redirect(url_for('index'))
                else:
                    flash('账号或密码错误！', 'error')
        finally:
            connection.close()
    #return render_template('login.html')
    return render_template('new_index.html')

#首页
@app.route('/index')
def index():
    #return render_template('index.html')
    return render_template('new_default.html')

    
#用户页面
@app.route('/user', methods=['GET', 'POST'])
def user():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT username, password,usertype FROM users"
            cursor.execute(sql)
            users = cursor.fetchall()
    finally:
        connection.close()
    return render_template('new_user.html', users=users) 

#密码页面
@app.route('/pwd', methods=['GET', 'POST'])
def pwd():
    if request.method == 'POST':
        username = session["username"]
        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 验证旧密码
                sql = "SELECT * FROM users WHERE username = %s AND password = %s"
                cursor.execute(sql, (username, oldpassword))
                user = cursor.fetchone()
                if not user:
                    flash('旧密码错误！', 'error')
                    return redirect(url_for('pwd'))
                # 更新密码
                sql = "UPDATE users SET password = %s WHERE username = %s"
                cursor.execute(sql, (newpassword, username))
            connection.commit()
            flash('密码修改成功！', 'success')
            return redirect(url_for('pwd'))
        finally:
            connection.close()
    return render_template('new_pwd.html')
#----------------------------------新增代码START
#删除用户
@app.route('/delete_user/<user_id>', methods=['GET'])
def delete_user_route(user_id):
    username = user_id
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM users where username = %s"
            cursor.execute(sql, (username))
        connection.commit()
        flash('删除用户成功！', 'success')
        return redirect(url_for('user'))
    finally:
        connection.close()
    return render_template('user.html')
#修改用户页面
@app.route('/user_edit/<user_id>', methods=['GET'])
def user_edit(user_id):
    username = user_id
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 检查账号和密码
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username))
            user = cursor.fetchone()
            if user:
                #成功继续执行
                return render_template('user_edit.html', user=user)
            else:
                flash('用户不存在!', 'error')
                return redirect(url_for('user'))
        connection.commit()
    finally:
        connection.close()
#修改用户页面---保存
@app.route('/user_edit_save', methods=['GET', 'POST'])
def user_edit_save():
    if request.method == 'POST':
        username = request.form['username']
        #password = request.form['password']
        usertype = request.form['usertype']
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 更新用户
                #sql = "UPDATE users SET password = %s,usertype = %s  WHERE username = %s"
                #cursor.execute(sql, (password, usertype,username))
                sql = "UPDATE users SET usertype = %s  WHERE username = %s"
                cursor.execute(sql, ( usertype,username))
            connection.commit()
            flash('用户修改成功！', 'success')
            return redirect(url_for('user'))
        finally:
            connection.close()
    return render_template('user_edit.html')
#添加用户
@app.route('/user_add', methods=['GET', 'POST'])
def user_add():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usertype = request.form['usertype']
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 检查用户名是否已存在
                sql = "SELECT * FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                if user:
                    flash('账号已存在！')
                    #return redirect(url_for('user_add'))
                    return redirect(url_for('user'))
                # 插入新用户
                sql = "INSERT INTO users (username, password,usertype) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, password,usertype))
            connection.commit()
            flash('用户添加成功！')
            return redirect(url_for('user'))
        finally:
            connection.close()
    #return render_template('user_add.html')
    return render_template('new_user.html')

# 记录登录日志
def record_login_log(username, ip_address):
    #login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 插入新用户
            sql = "INSERT INTO login_logs(username, ip_address, login_time) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, ip_address, login_time))
        connection.commit()
    finally:
        connection.close()
        #用户页面
@app.route('/login_logs', methods=['GET', 'POST'])
def login_logs():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT username, ip_address, login_time FROM login_logs"
            cursor.execute(sql)
            logs = cursor.fetchall()
    finally:
        connection.close()
    return render_template('new_login_logs.html', logs=logs)
#AI拍照
''' '''
@app.route('/ai_photo_old', methods=['GET', 'POST'])
def ai_photo_old():
    return render_template('new_ai_photo.html')

@app.route('/save_photo', methods=['POST'])
def save_photo():
    photo_data = request.form.get('photo')
    if photo_data:
        # 获取当前时间
        now = datetime.datetime.now()
        # 格式化时分秒毫秒
        time_str = now.strftime('%H%M%S%f')[:-3]
        # 去除数据前缀
        photo_data = photo_data.replace('data:image/png;base64,', '')
        import base64
        photo_path = os.path.join(UPLOAD_FOLDER, 'photo_'+time_str+'.png')
        with open(photo_path, 'wb') as f:
            f.write(base64.b64decode(photo_data))

        #record_ai_photo_log(session["username"] ,os.path.basename(photo_path))
        return '照片保存成功'
    return '未收到照片数据'
# 记录AI日志
def record_ai_photo_log(username, fileanme):
    login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO ai_photo(userid,username, fileanme, login_time,result,con_level) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (username,username, fileanme, login_time,'',0))#
        connection.commit()
    finally:
        connection.close()
@app.route('/ai_photo_logs', methods=['GET', 'POST'])
def ai_photo_logs():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT userid, username, fileanme,result,con_level,login_time FROM ai_photo"
            cursor.execute(sql)
            logs = cursor.fetchall()
    finally:
        connection.close()
    return render_template('new_ai_photo_logs.html', logs=logs)
 #----------------------------------新增代码END 
@app.route('/new_kzmb')
def new_kzmb():
    return render_template('new_kzmb.html')

@app.route('/new_echarts')
def new_echarts():
    connection = get_db_connection2()
    try:
        
        with connection.cursor() as cursor:
            sql = "Select con_level AS x_value,count(*) as y_value From  ai_photo t group by t.con_level"
            cursor.execute(sql)
            rows = cursor.fetchall()
            # 将查询结果转换为列表形式的坐标数据
            scatter_data = [list(row) for row in rows]
            print(scatter_data)
    finally:
        connection.close()
    return render_template('new_echarts.html', scatter_data=scatter_data) 
 
 #
#----------------------------------新增代码END
#AI
@app.route('/ai_photo', methods=['GET', 'POST'])
def ai_photo():
    return render_template('new_ai.html')
# AI处理接口
@app.route('/ai/process', methods=['POST'])
def ai_process():
    if 'image' not in request.files:
        return jsonify({"error": "请选择图片文件"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    # 保存上传的图片
    upload_folder = os.path.join(app.static_folder, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # 清理之前的临时文件
    temp_path = os.path.join(upload_folder, 'temp.png')
    result_temp_path = os.path.join(upload_folder, 'result_temp.png')

    # 使用统一的临时文件名保存上传的图片
    file.save(temp_path)

    try:
        st = ''
        # 使用AI模型处理图片
        processed_image = process_image(temp_path)

        # 保存处理后的图片，使用统一的结果文件名
        processed_image.save(result_temp_path)

        # 返回处理结果的 URL
        if ai_model.g_res is None:
            print("模型未正确初始化，无法进行预测。")
        else:
            names = ai_model.g_res.names
            cls = ai_model.g_res.boxes.cls.cpu().numpy()
            conf = ai_model.g_res.boxes.conf.cpu().numpy()
            confidence=0
            result_class_name=""
            for i in range(len(cls)):
                class_index = int(cls[i])
                class_name = names[class_index]
                confidence = conf[i]
            
                result_class_name=result_class_name+get_citrus_disease_info(class_name)+"<br/>"
            #result_class_name=class_name
            print(f"result_class_name: {result_class_name}")
            record_ai_photo_logx(session["username"] ,"",class_name,confidence) #XZ
        # 返回处理结果的 URL
        return jsonify({
            "result_class_name": result_class_name,
            "result": st + "处理成功",
            "original_image": url_for('static', filename='uploads/temp.png', _external=True),
            "processed_image": url_for('static', filename='uploads/result_temp.png', _external=True)
        })
    except Exception as e:
        print(e)
        return jsonify({"error": f"处理失败：{str(e)}"}), 500
    
def get_citrus_disease_info(disease_name):
    disease_info = {
        "Brown_Spot": {
            "预防": "加强果园管理，合理修剪，增强树势；及时排水，降低果园湿度；冬季清园，减少病原菌基数。",
            "治疗": "发病初期可选用苯醚甲环唑、戊唑醇等杀菌剂喷雾防治。"
        },
        "Citrus_Black_Spot": {
            "预防": "做好果园卫生，清除病叶、病果；合理施肥，增强树体抗病能力；适时喷药保护，在落花后及幼果期进行药剂防治。",
            "治疗": "可使用代森锰锌、多菌灵等杀菌剂进行喷雾防治。"
        },
        "Citrus_Canker": {
            "预防": "严格执行检疫制度，防止病菌传入；培育无病苗木；加强栽培管理，增施有机肥，避免偏施氮肥。",
            "治疗": "发病时可选用氢氧化铜、春雷霉素等药剂喷雾防治，同时及时剪除病枝、病叶、病果。"
        },
        "Citrus_Greasy_Spot": {
            "预防": "加强栽培管理，增强树势；做好冬季清园工作，减少越冬病菌；合理修剪，改善果园通风透光条件。",
            "治疗": "在春梢和秋梢发病初期，可选用吡唑醚菌酯、肟菌酯等杀菌剂喷雾防治。"
        },
        "Citrus_Scab": {
            "预防": "加强果园管理，合理密植，及时排水；冬季清园，铲除病原菌；在春梢萌芽期和幼果期进行药剂保护。",
            "治疗": "可选用甲基硫菌灵、百菌清等杀菌剂进行喷雾防治。"
        },
        "Greening": {
            "预防": "种植无病苗木；防治柑橘木虱，减少传毒媒介；加强果园管理，增强树势。",
            "治疗": "目前尚无有效的治疗方法，发现病株应及时挖除，集中烧毁，防止扩散。"
        },
        "Healthy": {
            "预防": "保持果园良好的生态环境，合理施肥、灌溉、修剪，做好病虫害监测，及时采取预防措施，维持柑橘树的健康状态。",
            "治疗": "无需治疗，保持预防措施即可。"
        },
        "Leprosis": {
            "预防": "加强检疫，防止病害传入；培育无病苗木；防治传毒昆虫，如蓟马等。",
            "治疗": "目前无特效治疗方法，主要是通过防治传毒昆虫来控制病害传播，同时加强树体营养，增强树势。"
        },
        "Orange_Scab": {
            "预防": "加强果园管理，增强树势；做好冬季清园工作，减少病原菌；在春雨和梅雨季节前进行药剂预防。",
            "治疗": "可选用氟环唑、苯甲·嘧菌酯等杀菌剂进行喷雾防治。"
        },
        "Sooty_Mold": {
            "预防": "防治柑橘蚜虫、蚧壳虫等刺吸式害虫，减少煤烟病的发生源头；加强果园通风透光，降低湿度。",
            "治疗": "及时防治害虫，可使用啶虫脒、噻嗪酮等药剂；同时用清水或弱碱性溶液清洗病叶、病果上的煤烟状物。"
        },
        "Xyloporosis": {
            "预防": "选用无病苗木；轮作换茬，与禾本科作物轮作；增施有机肥，改良土壤。",
            "治疗": "可使用阿维菌素、噻唑膦等药剂进行灌根处理。"
        }
        }
    if disease_name in disease_info:
        info = disease_info[disease_name]
        return f"病虫害名称: {disease_name}\n预防内容: {info['预防']}\n治疗方式: {info['治疗']}"
    else:
        return f"未找到 {disease_name} 的相关信息。"
    
def record_ai_photo_logx(username, fileanme,class_name,confidence):
    login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO ai_photo(userid,username, fileanme, login_time,result,con_level) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (username,username, fileanme, login_time,class_name,confidence))
        connection.commit()
    finally:
        connection.close()
###################
#AI_VID
@app.route('/ai_vid', methods=['GET', 'POST'])
def ai_vid():
    return render_template('ai_vid.html')
import  video_process_web 
# AI处理接口
@app.route('/ai/ai_process_video', methods=['POST'])
def ai_process_video():
    if 'video' not in request.files:
        return jsonify({"error": "请选择视频文件"}), 400
    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "未选择视频文件"}), 400
    if video:

 
        # 获取当前时间，精确到毫秒
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        # 分离文件名和扩展名
        filename, file_extension = os.path.splitext(video.filename)
        # 拼接新的文件名
        new_filename = f"{filename}_{current_time}{file_extension}"
        # 构建保存路径
        video_path = os.path.join('vid/temp', new_filename)

        #video_path = os.path.join('vid/temp', video.filename)
        video.save(video_path)
        #return '视频已成功保存到 ' + video_path
    try:
        #video_path = "vid/vid.mp4"
        output_path="output_video.mp4",
         # 生成随机数字
        random_number = current_time
        # 分离文件名和扩展名
        #filename, file_extension = os.path.splitext(output_path)
        filenamex="output_video"
        file_extensionx=".mp4"
        # 拼接新的文件名
        output_path = f"{filenamex}_{random_number}{file_extensionx}"
        #video_process_web.process_video(video_path, output_path ,skip_frames=2)
        video_process_web.process_video(video_path, "static/output_video.mp4",skip_frames=2)
        return jsonify({
            "result": f"处理成功！",
            "confidence": '',
            "label": '',
            "original_image": '',
            "processed_image": '',
        })
    except Exception as e:
        print(e)
        return jsonify({"error": f"处理失败：{str(e)}"}), 500
    ################
if __name__ == '__main__':
    app.run(debug=True)