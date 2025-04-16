from base import db
from base.com.vo.login_vo import LoginVO


class LoginDAO:

    # def check_login_username(self, login_vo):
    #     login_vo_list = LoginVO.query.filter_by(
    #         user_name=login_vo.user_name).all()
    #     return login_vo_list

    def view_login(self):
        login_vo_list = LoginVO.query.all()
        print("c+++++++", login_vo_list)
        return login_vo_list

    def insert_login(self, login_vo):
        db.session.add(login_vo)
        db.session.commit()

    def check_login_username(self, login_vo):
        login_vo_list = LoginVO.query.filter_by(
            login_username=login_vo.login_username).all()
        return login_vo_list

    # def view_login(self):
    #     login_vo_list = LoginVO.query.all()
    #     return login_vo_list

    def update_login(self, login_vo):
        db.session.merge(login_vo)
        db.session.commit()

    def login_validate_username(self, login_vo):
        login_vo_list = LoginVO.query.filter_by(
            login_username=login_vo.login_username).all()
        return login_vo_list

    def login_validate_password(self, login_vo):
        login_vo_list = LoginVO.query.filter_by(login_password=login_vo.login_password).all()
        return login_vo_list

    def find_login_id(self, login_vo):
        login_vo_list = LoginVO.query.filter_by(login_username=login_vo.login_username).all()[-1].login_id
        return login_vo_list
