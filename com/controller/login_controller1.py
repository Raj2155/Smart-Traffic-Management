from datetime import timedelta

import bcrypt
from flask import render_template, request, redirect, flash, make_response, url_for

from base import app
from base.com.dao.login_dao import LoginDAO
from base.com.dao.video_dao import VideoDAO
from base.com.vo.login_vo import LoginVO


# @app.route('/')
# def login():
#     return render_template('admin/login.html')


# @app.route('/validate_login', methods=['POST', 'GET'])
# def view_login():
#     session['login_username'] = request.form.get("username")
#     session['login_password'] = request.form.get("password")
#     login_vo = LoginVO()
#     login_dao = LoginDAO()
#     login_vo_list = login_dao.view_login()
#     login_list = [login_vo_list.as_dict() for login_vo_list in login_vo_list]
#     print('login_vo_list+++++', login_vo_list)
#     print('login_list+++++', login_list[0])
#     print('login_list2+++++', login_list[1])
#     if (login_list[0]['user_name'] == session['login_username'] and login_list[0][
#
#         'password']
#             == session['login_password']):
#         return render_template("admin/index.html")
#
#     # login_vo_list = login_dao.check_login_username(login_vo)
#     # login_list = [i.as_dict() for i in login_vo_list]
#     # len_login_list = len(login_list)
#     else:
#         error_message = 'Username or Password is incorrect!!'
#         flash(error_message)
#         return redirect("/")

# @app.route('/validate_login', methods=['POST', 'GET'])
# def validate_login():
#     if request.method == "POST":
#         # try:
#         global_loginvo_list = []
#         global_login_secretkey_set = []
#
#         login_username = request.form.get("username")
#         login_password = request.form.get("password").encode("utf-8")
#         print("login_username+++++++", login_username)
#         print("login_password++++++++++", login_password)
#         login_vo = LoginVO()
#         login_dao = LoginDAO()
#
#         login_vo.user_name = login_username
#
#         login_vo_list = login_dao.check_login_username(login_vo)
#         login_list = [i.as_dict() for i in login_vo_list]
#         len_login_list = len(login_list)
#
#         if len_login_list == 0:
#             error_message = 'Username or Password is incorrect!!'
#             flash(error_message)
#             return redirect("/")
#         else:
#             login_id = login_list[0]['login_id']
#             login_username = login_list[0]['user_name']
#             login_role = login_list[0]['login_role']
#             login_secretkey = login_list[0]['login_secretkey']
#             hashed_login_password = login_list[0]['password'].encode("utf-8")
#             print("login_username&&&&&&", login_username)
#             print("login_secretkey&&&&&&", login_secretkey)
#             print("login_password********", hashed_login_password)
#             print("%%%%%%%%%%%%%%", login_id)
#             if bcrypt.checkpw(login_password, hashed_login_password):
#                 login_vo_dict = {
#                     login_secretkey: {'login_username': login_username,
#                                       'login_role': login_role,
#                                       'login_id': login_id}}
#
#                 if len(global_loginvo_list) != 0:
#                     for i in global_loginvo_list:
#                         temp_list = list(i.keys())
#                         global_login_secretkey_set.add(temp_list[0])
#                     login_secretkey_list = list(global_login_secretkey_set)
#                     if login_secretkey not in login_secretkey_list:
#                         global_loginvo_list.append(login_vo_dict)
#                 else:
#                     global_loginvo_list.append(login_vo_dict)
#                 if login_role == 'admin':
#                     response = make_response(
#                         redirect(url_for('index')))
#                     response.set_cookie('login_secretkey',
#                                         value=login_secretkey,
#                                         max_age=timedelta(minutes=30))
#                     response.set_cookie('login_username', value=login_username,
#                                         max_age=timedelta(minutes=30))
#                     # response.set_cookie('login_id',
#                     #                     value=login_id.to_bytes(2,'big'),
#                     #                     max_age=timedelta(minutes=30))
#
#                     return response
#                 else:
#                     return redirect(url_for('admin_logout_session'))
#             else:
#                 error_message = 'Username or Password is incorrect!!'
#                 flash(error_message)
#                 return redirect("/")
#
#     # except Exception as ex:
#     #     return str(ex)
#
#
# @app.route('/login_session')
# def admin_login_session():
#     # try:
#     global_loginvo_list = []
#     login_role_flag = ""
#     login_secretkey = request.cookies.get('login_secretkey')
#     if login_secretkey is None:
#         return redirect('/')
#     for i in global_loginvo_list:
#         if login_secretkey in i.keys():
#             if i[login_secretkey]['login_role'] == 'admin':
#                 login_role_flag = "admin"
#     return login_role_flag


# except Exception as ex:
#     return str(ex)


# @app.route("/logout_session", methods=['GET'])
# def admin_logout_session():
#     # try:
#     global_loginvo_list = []
#     login_secretkey = request.cookies.get('login_secretkey')
#     login_username = request.cookies.get('login_username')
#     response = make_response(redirect('/'))
#     if login_secretkey is not None and login_username is not None:
#         response.set_cookie('login_secretkey', login_secretkey, max_age=0)
#         response.set_cookie('login_username', login_username, max_age=0)
#         for i in global_loginvo_list:
#             if login_secretkey in i.keys():
#                 global_loginvo_list.remove(i)
#                 break
#     return response


# except Exception as ex:
#     return str(ex)


# @app.route('/index')
# def index():
#     # if admin_login_session() == "admin":
#     video_dao = VideoDAO()
#
#     total_count = video_dao.total_count()
#     video_list = [i.as_dict() for i in total_count]
#
#     # total entry count
#     total_entry_count = []
#     for i in video_list:
#         count = int(i.get('entry_count'))
#         total_entry_count.append(count)
#     sum_entry = sum(total_entry_count)
#
#     # total exit count
#     total_exit_count = []
#     for i in video_list:
#         count = int(i.get('exit_count'))
#         total_exit_count.append(count)
#     sum_exit = sum(total_exit_count)
#
#     print(">>>>>>>>>>>>>>>>>>>>>>>", video_list)
#
#     return render_template('admin/index.html', entry=sum_entry,
#                            exit=sum_exit)
# else:
#     return admin_logout_session()
# @app.route('/logout', methods=['GET', 'POST'])
# def logout():
#     session.pop('login_username', None)
#     # return redirect(url_for('index'))
#     # session.clear()
#     return redirect("/")
