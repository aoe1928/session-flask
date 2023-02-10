from flask import request, render_template, url_for, redirect, session
from .models import User, Bbs
from index import app, db, bcrypt
from sqlalchemy import desc, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text
from datetime import datetime
import os

# app.secret_key = 'abcdefghijklmn'
# app.permanent_session_lifetime = timedelta(minutes=3) 


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # ログイン試行
        if User.query.filter_by(email=email).first():
            conn = User.query.filter_by(email=email).first()
            if(conn and bcrypt.check_password_hash(conn.password, password)):
                session.permenet = True
                session["id"] = email
                return redirect(url_for("login_"))
            else:
                message = "パスワードが間違っています"
                return render_template("index.html", message=message)
        # ユーザーが存在しない場合登録処理
        user = User(email=email, password=password)
        db.session.add(user)
        try:
            # ユーザーが存在しない場合の処理、登録
            db.session.commit()
        except IntegrityError:
            # 同名のメールアドレスが登録されていた場合
            message = 'メールアドレスが登録済み'
            return render_template("index.html", message=message)
        session.permenet = True
        session["id"] = email
        return redirect(url_for("login_"))
    else:
        if "id" in session:
            return render_template("login.html", id=session["id"])
        message = "ログインしてください"
        return render_template("index.html", message=message)


@app.route("/login", methods=["GET","POST"])
def login_():
    if "id" in session: 
        return render_template("login.html", id=session["id"])
    return render_template("index.html", message="ログインしてください") 


@app.route("/logout", methods=["GET"])
def logout():
    session.pop('id',None)
    session.clear()
    return redirect("/")


@app.route("/bbs", methods=["GET", "POST"])
def bbs():
    if request.method == "GET":
        flag = False
        conn = Bbs.query.order_by(desc(Bbs.id)).all()
        bbs_list = []
        for c in conn:
            bbs_list.append([c.email, c.text, c.date])
        if "id" in session:
            flag = True
            return render_template("bbs.html", flag=flag, bbs_list=bbs_list)
        else:
            return render_template("bbs.html", bbs_list=bbs_list)
    
    else:
        text = request.form.get("text")
        time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        user = session["id"]
        for s in [text, time]:
            if len(s) == 0:
                # 0文字は許可できない
                return render_template("index.html", message="空白の投稿は許可されていません")
        db.session.add(Bbs(email=user, text=text, date=time))
        db.session.commit()
        return redirect("/bbs")


@app.route('/regist2', methods=['GET', 'POST'])
def login2():
    if request.method == "GET":
        return render_template("regist2.html")
    else:
        email = request.form.get("email")
        password = bcrypt.generate_password_hash(request.form.get("password")).decode("utf-8")
        # password = request.form.get("password")
        # data = {"email": f"{email}", "password": f"{password}"}
        statement = text(f"""insert into User(email, password) values ('{email}', '{password}')""")
        engine = create_engine(os.environ['DATABASE_URL'])
        try:
            engine.execute(statement=statement)
        except IntegrityError as e:
            print(e)
            comment = "エラーが起こりました"
            return render_template("index.html", comment=comment)
        comment = "登録出来ました"
        return render_template("index.html", comment=comment)


@app.route('/users', methods=['GET'])
def users():
    search_user = request.args.get("user")
    engine = create_engine(os.environ['DATABASE_URL'])
    statement = text(f"""select email from user where email like '%{search_user}%'""")
    try:
        res = engine.execute(statement=statement)
    except IntegrityError as e:
        print(e)
        comment = "エラーが起こりました"
        return render_template("index.html", comment=comment)
    user_list = []
    for r in res.fetchall():
        r = r[0]
        user_list.append(r)
    return render_template("users.html", user_list=user_list)


@app.route('/delete_post')
def delete_post():
    if "id" not in session:
        return render_template("index.html", message="ログインしてください")
    else:
        user = session["id"]
        Bbs.query.filter_by(email=user).delete()
        db.session.commit()
        return render_template("index.html", message="削除しました")


@app.route('/debug', methods=['GET'])
def debug():
    return "debug"

