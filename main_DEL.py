import datetime
import os
from flask import Flask, render_template, request, flash, redirect, url_for, session
import pymysql
from config import Config
from ai_model import process_image
from flask import jsonify

 
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
    return render_template('register.html')

#默认登录页
@app.route('/')
def login_page():
    return render_template('login.html')

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
    return render_template('login.html')

#首页
@app.route('/index')
def index():
    return render_template('index.html')
    
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
    return render_template('user.html', users=users)

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
    return render_template('pwd.html')
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
        password = request.form['password']
        usertype = request.form['usertype']
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 更新用户
                sql = "UPDATE users SET password = %s,usertype = %s  WHERE username = %s"
                cursor.execute(sql, (password, usertype,username))
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
                    return redirect(url_for('user_add'))
                # 插入新用户
                sql = "INSERT INTO users (username, password,usertype) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, password,usertype))
            connection.commit()
            flash('用户添加成功！')
            return redirect(url_for('user'))
        finally:
            connection.close()
    return render_template('user_add.html')

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
    return render_template('login_logs.html', logs=logs)

#AI
@app.route('/ai_photo', methods=['GET', 'POST'])
def ai_photo():
    return render_template('ai.html')

@app.route('/save_photo', methods=['POST'])
def save_photo():
    photo_data = request.form.get('photo')
    if photo_data:
        # 去除数据前缀
        photo_data = photo_data.replace('data:image/png;base64,', '')
        import base64
        photo_path = os.path.join(UPLOAD_FOLDER, 'photo.png')
        with open(photo_path, 'wb') as f:
            f.write(base64.b64decode(photo_data))
        return '照片保存成功'
    return '未收到照片数据'
 #----------------------------------新增代码END
# 创建一个字典来存储产品名称和价格
product_prices = {
    "AW cola": 11,
    "Beijing Beef": 12,
    "Chow Mein": 13,
    "Fried Rice": 14,
    "Hashbrown": 15,
    "Honey Walnut Shrimp": 16,
    "Kung Pao Chicken": 17,
    "String Bean Chicken Breast": 18,
    "Super Greens": 19,
    "The Original Orange Chicken": 20,
    "White Steamed Rice": 21,
    "black pepper rice bowl": 22,
    "burger": 23,
    "carrot_eggs": 24,
    "cheese burger": 25,
    "chicken waffle": 26,
    "chicken_nuggets": 27,
    "chinese_cabbage": 28,
    "chinese_sausage": 29,
    "crispy corn": 30,
    "curry": 31,
    "french fries": 32,
    "fried chicken": 33,
    "fried_chicken": 34,
    "fried_dumplings": 35,
    "fried_eggs": 36,
    "mango chicken pocket": 37,
    "mozza burger": 38,
    "mung_bean_sprouts": 39,
    "nugget": 40,
    "perkedel": 41,
    "rice": 42,
    "sprite": 43,
    "tostitos cheese dip sauce": 44,
    "triangle_hash_brown": 45,
    "water_spinach": 46
}
# 定义一个函数，通过产品名称获取价格
def get_price(product_name):
    return product_prices.get(product_name)

import  ai_model
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
        return jsonify({
            "result_class_name": "",
            "result": st + "处理成功",
            "original_image": url_for('static', filename='uploads/temp.png', _external=True),
            "processed_image": url_for('static', filename='uploads/result_temp.png', _external=True)
        })
    except Exception as e:
        print(e)
        return jsonify({"error": f"处理失败：{str(e)}"}), 500


#if __name__ == '__main__':
#    app.run(debug=True)