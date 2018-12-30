# -*- coding:utf-8 -*-

__author__ = u'Jiang Wen'
from flask import render_template, flash, request, abort, redirect, url_for, g, jsonify
from app import app, db, lm, DEBUGGING  # , csv_set
from flask_login import login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from app.models import test_init, User, Course, Homework, TakingClass, StudentHomework, Post, Message
from app.forms import LoginForm, SignUpForm, AddCourseForm
from flask_uploads import *
from sqlalchemy.sql import and_
from sqlalchemy import func
import json
import requests

Bootstrap(app)


@app.before_first_request
def init_view():
    # Uncomment to recreate database every time
    db.drop_all()
    db.create_all()  # Do not recreate mysql database.
    test_init()
    db.session.commit()

    print(User.query.all())
    print(Course.query.all())
    print(Homework.query.all())
    print(TakingClass.query.all())
    print(Post.query.all())
    print(Message.query.all())

    # Add login guider
    lm.login_view = url_for('login')
    lm.login_message = "Please login"
    lm.login_message_category = 'info'


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(uid):
    return User.query.get(uid)


class Total:
    def __init__(self, name, teacher, time, imgUPL, courseDetail):
        self.name = name
        self.teacher = teacher
        self.time = time
        self.imgURL = imgUPL
        self.courseDetail = courseDetail


@app.route('/index.html')
def index():
    flash('Hello, test flash', 'success')
    # print(g.user.email)
    takings = TakingClass.query.filter_by(student_id=g.user.id).all()

    courses = []
    for taking in takings:
        course = Course.query.filter_by(id=taking.course_id).first()
        courses.append(course)

    # class Total:
    #     def __init__(self, name, teacher, time, imgUPL, courseDetail):
    #         self.name = name
    #         # self.location = "location"
    #         self.teacher = teacher
    #         self.time = time
    #         self.imgURL = imgUPL
    #         self.courseDetail = courseDetail

    # flash ( 'Hello %s, you have logged in.' % current_user.get_id (), 'success' )

    total = []
    for course in courses:
        onecourse = Total(course.name, course.teacher_id, course.time, course.course_url, course.description)
        total.append(onecourse)
    return render_template("index.html", Total=total)


@app.route('/Tindex.html', methods=['GET', 'POST'])
def Tindex():
    form = AddCourseForm()
    # flash ( 'Hello %s, you have logged in.' % current_user.get_id (), 'success' )
    flash('Hello, test flash', 'success')
    courses = Course.query.filter_by(teacher_id=g.user.id).all()
    total = []
    for course in courses:
        onecourse = Total(course.name, course.teacher_id, course.time, course.course_url, course.description)
        total.append(onecourse)

    if form.validate_on_submit():
        print("a")
        try:
            # print("b")
            course = Course.query.filter_by(id=form.courseID.data).first()
            if not course is None:
                error = 'Course has registered!'
                return render_template('Tindex.html')
            else:
                filename = form.picture.data.filename
                print(filename)
                # 将上传的文件保存到服务器;
                form.picture.data.save(filename)
                db.session.add(
                    Course(form.courseID.data, form.coursename.data, g.user.id, filename, form.time.data,
                           form.description.data))
                db.session.commit()
                print(Course.query.all())
                flash('The course is added successfully!')
                return redirect(url_for('Tindex'))
        except Exception as e:
            flash(e, 'danger')
    return render_template("Tindex.html", Total=total, form=form)


@app.route('/contact.html')
def contact():
    return render_template('contact.html')


@app.route('/courseDemo.html')
def courseDemo():
    class CourseInfo:
        def __init__(self):
            self.name = 'This is name'
            self.details = 'This id details balabala'

    return render_template('courseDemo.html', courseInfo=CourseInfo())


@app.route('/forum.html')
def forum():
    class Total:
        def __init__(self):
            self.name = 'This is name'
            self.id = 'This is id'
            self.details = 'This is details balabala'

    return render_template('forum.html', Total=[Total()] * 10)


@app.route('/homework.html')
def homework():
    class HomeworkInfo:
        def __init__(self):
            self.name = 'This is name'
            self.url = "homeworkDemo.html"
            self.grade = 99

    return render_template('homework.html', Total=[HomeworkInfo()] * 10)


@app.route('/homeworkDemo.html')
def homeworkDemo():
    class HomeworkInfo:
        def __init__(self):
            self.name = 'This is name'
            self.details = "fdasfasdfasdfasdfasd"

    return render_template('homeworkDemo.html', homework=HomeworkInfo())


@app.route('/info.html')
def info():
    class Info:
        def __init__(self):
            self.name = 'This is name'
            self.details = "fdasfasdfasdfasdfasd"

    return render_template('info.html', Total=[Info()] * 10)


@app.route('/media.html')
def media():
    class Info:
        def __init__(self):
            self.url = 'courseDemo'
            self.img = "../static/uploads/course_01.jpg"

    return render_template('media.html', Total=[Info()] * 10)


@app.route('/signUp.html', methods=['GET', 'POST'])
def signUp():
    form = SignUpForm()
    # print("aaaaa")
    if form.validate_on_submit():
        # print("OK!!")
        try:
            user = User.query.filter_by(id=form.user.data).first()
            if not user is None:
                error = 'User has registered!'
                return render_template('signUp.html')
            else:
                db.session.add(
                    User(form.user.data, form.name.data, form.password.data, form.email.data, form.userType.data))
                db.session.commit()
        except Exception as e:
            flash(e, 'danger')

        print(User.query.all())
    return render_template('signUp.html', form=form)


@app.route('/TcourseDemo.html')
def TcourseDemo():
    return render_template('TcourseDemo.html')


@app.route('/Thomework.html')
def Thomework():
    return render_template('Thomework.html')


@app.route('/Tinfo.html')
def Tinfo():
    return render_template('Tinfo.html')


@app.route('/Tmedia.html')
def Tmedia():
    return render_template('Tmedia.html')


# @app.route('/signUpp.html')
# def signUpp():
#     return render_template('signUp.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # if g.user is not None and g.user.is_authenticated:
    #     flash("You have logged in to system")
    #     return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(id=form.username.data).first()
            if user is None:
                error = 'Invalid username'
            elif not user.check_password_hash(form.password.data):
                error = 'Invalid password'
            else:
                login_user(user=user, remember=form.remember.data)
                print(user.user_type)
                if user.user_type == 'student':
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for("Tindex"))
        except Exception as e:
            # flash ( 'login fail', 'primary' )
            flash(e, 'danger')

    elif request.method == 'POST':
        flash('Invalid input', 'warning')
    if error is not None:
        flash(error, category='danger')
    return render_template('login.html', form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()  # 登出用户
    flash("Logout successful", category='success')
    return redirect(url_for('index'))
