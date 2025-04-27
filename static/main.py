import datetime
import os
from flask import Flask, render_template, request, flash, redirect, url_for, session
import pymysql
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


@app.route('/ai_photo', methods=['GET', 'POST'])
def ai_photo():
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

        record_ai_photo_log(session["username"] ,os.path.basename(photo_path))
        return '照片保存成功'
    return '未收到照片数据'
# 记录AI日志
def record_ai_photo_log(username, fileanme):
    login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO ai_photo(userid,username, fileanme, login_time,result,con_level) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (username,username, fileanme, login_time,'',''))
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
if __name__ == '__main__':
    app.run(debug=True)