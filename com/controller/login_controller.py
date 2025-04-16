import random
import smtplib
from datetime import timedelta, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps

import bcrypt
import httpagentparser
import jwt
from flask import render_template, redirect, request, url_for, make_response, \
    flash, session

from base import app
# from base.com.dao.complain_dao import ComplainDAO
from base.com.dao.device_info_dao import DeviceInfoDAO
# from base.com.dao.feedback_dao import FeedbackDAO
from base.com.dao.login_dao import LoginDAO
# from base.com.dao.product_dao import ProductDAO
# from base.com.dao.user_dao import UserDAO
from base.com.vo.device_info_vo import DeviceInfoVO

from base.com.dao.video_dao import VideoDAO
from base.com.vo.login_vo import LoginVO


def get_client_identity():
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

    agent = request.environ.get('HTTP_USER_AGENT')
    browser = httpagentparser.detect(agent)
    if not browser:
        browser = agent.split('/')[0]
    else:
        browser = browser['browser']['name']
    return "{}:{}".format(ip_addr, browser)


def insert_client_identity(login_id):
    login_vo = LoginVO()
    login_vo.login_id = login_id

    device_info_dao = DeviceInfoDAO()
    device_info_vo = DeviceInfoVO()

    device_list = device_info_dao.search_device(login_vo)

    for device in device_list:
        if bcrypt.checkpw(get_client_identity().encode("utf-8"),
                          device.device_identity.encode("utf-8")):
            device_info_vo = device
            break

    hashed_client_identity = bcrypt.hashpw(
        get_client_identity().encode("utf-8"),
        bcrypt.gensalt(rounds=12))
    device_info_vo.device_identity = hashed_client_identity
    device_info_vo.device_login_id = login_id

    device_info_dao.insert_device_info(device_info_vo)


def refresh_token(fn):
    # try:
        refreshtoken = request.cookies.get('refreshtoken')

        if refreshtoken is not None:
            data = jwt.decode(refreshtoken, app.config['SECRET_KEY'], 'HS256')

            login_vo = LoginVO()
            login_dao = LoginDAO()

            login_vo.login_username = data['public_id']

            login_vo_list = login_dao.check_login_username(login_vo)

            device_info_dao = DeviceInfoDAO()

            device_list = device_info_dao.search_device(login_vo_list[0])

            for device in device_list:
                print('In Token Refresh')
                if bcrypt.checkpw(get_client_identity().encode("utf-8"),
                                  device.device_identity.encode("utf-8")):
                    print('Device Matched')
                    response = make_response(fn())
                    response.set_cookie('accesstoken',
                                        value=jwt.encode({
                                            'public_id': login_vo_list[
                                                0].login_username,
                                            'role': login_vo_list[
                                                0].login_role,
                                            'exp': datetime.utcnow() + timedelta(
                                                seconds=30)
                                        }, app.config['SECRET_KEY'],
                                            'HS256'),
                                        max_age=timedelta(seconds=30))
                    refresh = jwt.encode({
                        'public_id': login_vo_list[0].login_username,
                        'exp': datetime.utcnow() + timedelta(hours=1)
                    }, app.config['SECRET_KEY'], 'HS256')

                    print('Token Refreshed Successfully')
                    response.set_cookie('refreshtoken',
                                        value=refresh,
                                        max_age=timedelta(hours=1))
                    return response
            else:
                error_message = 'We Encounterd Malicious Activity Please Re-Login'
                flash(error_message)
                return admin_logout_session(login_vo.login_username)
        else:
            error_message = 'Unauthorized Access'
            flash(error_message)
            return admin_logout_session()
    # except Exception as ex:
    #     print('Exception in Refreshing Token', ex)
    #     error_message = 'Session expired'
    #     flash(error_message)
    #     return admin_logout_session()


def login_required(role):
    def inner(fn):
        @wraps(fn)
        def decorator():
            # try:
                accesstoken = request.cookies.get('accesstoken')

                if accesstoken is None:
                    return refresh_token(fn)
                else:
                    data = jwt.decode(accesstoken, app.config['SECRET_KEY'],
                                      'HS256')
                    login_vo = LoginVO()
                    login_dao = LoginDAO()

                    login_vo.login_username = data['public_id']

                    login_vo_list = login_dao.check_login_username(login_vo)
                    if login_vo_list is not None:
                        login_list = [i.as_dict() for i in login_vo_list]

                        if login_list[0]['login_status'] == 1 and data[
                            'role'] == role:
                            return fn()
                        else:
                            return redirect('/')
                    else:
                        error_message = 'Unauthorized Access'
                        flash(error_message)
                        return redirect('/')
            # except Exception as ex:
            #     print(ex)
            #     return refresh_token(fn)

        return decorator

    return inner


@app.route('/', methods=['GET'])
def admin_load_login():
    # try:
        return render_template('admin/login.html')
    # except Exception as ex:
    #     print("admin_load_login route exception occured>>>>>>>>>>", ex)
    #     return render_template('user/viewError.html', ex=ex)


@app.route("/admin/validate_login", methods=['POST'])
def admin_validate_login():
    # try:
        login_username = request.form.get('loginUsername')
        login_password = request.form.get('loginPassword').encode("utf-8")

        login_vo = LoginVO()
        login_dao = LoginDAO()

        login_vo.login_username = login_username

        login_vo_list = login_dao.check_login_username(login_vo)
        login_list = [i.as_dict() for i in login_vo_list]
        len_login_list = len(login_list)

        if len_login_list == 0:
            error_message = 'username is incorrect !'
            flash(error_message)
            return redirect('/')
        elif not login_list[0]['login_status']:
            error_message = 'You have been temporarily blocked by website admin !'
            flash(error_message)
            return redirect('/')
        else:
            login_username = login_list[0]['login_username']
            login_role = login_list[0]['login_role']
            hashed_login_password = login_list[0]['login_password'].encode(
                "utf-8")
            if bcrypt.checkpw(login_password, hashed_login_password):

                insert_client_identity(login_list[0]['login_id'])

                if login_role == 'admin':
                    response = make_response(
                        redirect(url_for('index')))
                    response.set_cookie('accesstoken',
                                        value=jwt.encode({
                                            'public_id': login_username,
                                            'role': login_role,
                                            'exp': datetime.utcnow() + timedelta(
                                                seconds=30)
                                        }, app.config['SECRET_KEY'], 'HS256'),
                                        max_age=timedelta(seconds=30))
                    refresh = jwt.encode({
                        'public_id': login_username,
                        'exp': datetime.utcnow() + timedelta(hours=1)
                    }, app.config['SECRET_KEY'], 'HS256')

                    response.set_cookie('refreshtoken',
                                        value=refresh,
                                        max_age=timedelta(hours=1))
                    return response

                elif login_role == 'user':
                    response = make_response(
                        redirect(url_for('user_load_dashboard')))
                    response.set_cookie('accesstoken',
                                        value=jwt.encode({
                                            'public_id': login_username,
                                            'role': login_role,
                                            'exp': datetime.utcnow() + timedelta(
                                                seconds=30)
                                        }, app.config['SECRET_KEY'], 'HS256'),
                                        max_age=timedelta(seconds=30))
                    refresh = jwt.encode({
                        'public_id': login_username,
                        'exp': datetime.utcnow() + timedelta(hours=1)
                    }, app.config['SECRET_KEY'], 'HS256')
                    response.set_cookie('refreshtoken',
                                        value=refresh,
                                        max_age=timedelta(hours=1))
                    return response

                else:
                    return admin_logout_session()
            else:
                error_message = 'password is incorrect !'
                flash(error_message)
                return redirect('/')
    # except Exception as ex:
    #     print("admin_validate_login route exception occured>>>>>>>>>>", ex)
    #     return redirect(url_for('admin_logout_session'))


@app.route('/index')
@login_required('admin')
def index():
    # if admin_login_session() == "admin":
    video_dao = VideoDAO()

    total_count = video_dao.total_count()
    video_list = [i.as_dict() for i in total_count]

    # total entry count
    total_entry_count = []
    for i in video_list:
        count = int(i.get('entry_count'))
        total_entry_count.append(count)
    sum_entry = sum(total_entry_count)

    # total exit count
    total_exit_count = []
    for i in video_list:
        count = int(i.get('exit_count'))
        total_exit_count.append(count)
    sum_exit = sum(total_exit_count)

    print(">>>>>>>>>>>>>>>>>>>>>>>", video_list)

    return render_template('admin/index.html', entry=sum_entry,
                           exit=sum_exit)


@app.route('/user/load_dashboard', methods=['GET'])
def user_load_dashboard():
    try:
        return render_template('user/index.html')
    except Exception as ex:
        print("user_load_dashboard route exception occured>>>>>>>>>>", ex)
        return render_template('user/viewError.html', ex=ex)


@app.route("/admin/logout_session", methods=['GET'])
def admin_logout_session(*user_name):
    # try:
        if len(user_name) != 0 and user_name[0] is not None:
            login_vo = LoginVO()
            login_dao = LoginDAO()
            device_info_dao = DeviceInfoDAO()

            login_vo.login_username = user_name[0]

            login_vo_list = login_dao.check_login_username(login_vo)

            login_id = login_vo_list[0].login_id
            device_info_dao.delete_all_device(login_id)

            response = make_response(redirect('/'))
            response.set_cookie('accesstoken', max_age=0)
            response.set_cookie('refreshtoken', max_age=0)
            return response
        elif request.cookies.get('refreshtoken') is not None:
            refreshtoken = request.cookies.get('refreshtoken')

            data = jwt.decode(refreshtoken, app.config['SECRET_KEY'], 'HS256')

            login_vo = LoginVO()
            login_dao = LoginDAO()
            device_info_dao = DeviceInfoDAO()
            device_info_vo = DeviceInfoVO()

            login_vo.login_username = data['public_id']

            login_vo_list = login_dao.check_login_username(login_vo)
            login_vo = login_vo_list[0]

            device_list = device_info_dao.search_device(login_vo)

            if len(device_list) != 0:
                for device in device_list:
                    if bcrypt.checkpw(get_client_identity().encode("utf-8"),
                                      device.device_identity.encode("utf-8")):
                        device_info_vo = device
                        break

                device_info_dao.delete_device(device_info_vo)

            response = make_response(redirect('/'))
            response.set_cookie('accesstoken', max_age=0)
            response.set_cookie('refreshtoken', max_age=0)
            return response
        else:
            response = make_response(redirect('/'))
            response.set_cookie('accesstoken', max_age=0)
            response.set_cookie('refreshtoken', max_age=0)

            return response

    # except Exception as ex:
    #     print("admin_logout_session route exception occured>>>>>>>>>>", ex)
    #     return render_template('user/viewError.html', ex=ex)


@app.route("/admin/block_user", methods=['GET'])
@login_required('admin')
def admin_block_user():
    # try:
        login_vo = LoginVO()
        login_dao = LoginDAO()

        login_id = request.args.get('loginId')
        login_vo.login_id = login_id
        login_vo.login_status = False
        login_dao.update_login(login_vo)
        return redirect("/admin/view_user")

    # except Exception as ex:
    #     print("admin_block_user route exception occured>>>>>>>>>>", ex)
    #     return render_template('admin/viewError.html', ex=ex)


@app.route("/admin/unblock_user", methods=['GET'])
@login_required('admin')
def admin_unblock_user():
    # try:
        login_vo = LoginVO()
        login_dao = LoginDAO()

        login_id = request.args.get('loginId')
        login_vo.login_id = login_id
        login_vo.login_status = True
        login_dao.update_login(login_vo)
        return redirect('/admin/view_user')
    # except Exception as ex:
    #     print("admin_unblock_user route exception occured>>>>>>>>>>", ex)
    #     return render_template('admin/viewError.html', ex=ex)


@app.route('/user/load_forget_password', methods=['GET'])
def user_load_forget_password():
    try:
        return render_template('user/forgetPassword.html')
    except Exception as ex:
        print("user_load_forget_password route exception occured>>>>>>>>>>",
              ex)
        return render_template('user/viewError.html', ex=ex)


@app.route('/user/validate_login_username', methods=['post'])
def user_validate_login_username():
    try:
        login_username = request.form.get("loginUsername")
        print('login_username >>>>', login_username)
        login_dao = LoginDAO()
        login_vo = LoginVO()

        login_vo.login_username = login_username
        login_vo_list = login_dao.login_validate_username(login_vo)
        login_list = [i.as_dict() for i in login_vo_list]
        print("login_list >>>>>", login_list)
        len_login_list = len(login_list)
        if len_login_list == 0:
            error_message = 'username is incorrect !'
            flash(error_message)
            return redirect(url_for('user_load_forget_password'))
        else:
            login_id = login_list[0]['login_id']
            session['session_login_id'] = login_id
            login_username = login_list[0]['login_username']
            sender = "noreplypython@yahoo.com"
            receiver = login_username
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = "PYTHON OTP"
            otp = random.randint(1000, 9999)
            session['session_otp_number'] = otp
            message = str(otp)
            msg.attach(MIMEText(message, 'plain'))
            server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
            server.starttls()
            server.login(sender, "dbzivjinwbndvvey")
            text = msg.as_string()
            server.sendmail(sender, receiver, text)
            server.quit()
            return render_template('user/otpValidation.html')
    except Exception as ex:
        print("user_validate_login_username route exception occured>>>>>>>>>>",
              ex)
        return render_template('user/viewError.html', ex=ex)


@app.route('/user/validate_otp_number', methods=['POST'])
def user_validate_otp_number():
    try:
        otp_number = int(request.form.get("otpNumber"))
        session_otp_number = session.get('session_otp_number')
        if otp_number == session_otp_number:
            return render_template('user/resetPassword.html')
        else:
            session.clear()
            error_message = 'otp is incorrect !'
            flash(error_message)
            return redirect(url_for('admin_load_forget_password'))
    except Exception as ex:
        print("user_validate_otp_number route exception occured>>>>>>>>>>", ex)
        return render_template('user/viewError.html', ex=ex)


@app.route('/user/insert_reset_password', methods=['POST'])
def user_insert_reset_password():
    try:
        login_password = request.form.get("loginPassword")
        salt = bcrypt.gensalt(rounds=12)
        hashed_login_password = bcrypt.hashpw(login_password.encode("utf-8"),
                                              salt)
        login_id = session.get("session_login_id")
        login_dao = LoginDAO()
        login_vo = LoginVO()
        login_vo.login_id = login_id
        login_vo.login_password = hashed_login_password
        login_dao.update_login(login_vo)
        return redirect('/')
    except Exception as ex:
        print("user_insert_reset_password route exception occured>>>>>>>>>>",
              ex)
        return render_template('user/viewError.html', ex=ex)

@app.route('/about')
def about():
    try:
        return render_template("admin/about.html")
    except Exception as ex:
        print("user_insert_reset_password route exception occured>>>>>>>>>>",
              ex)
        return render_template('user/viewError.html', ex=ex)