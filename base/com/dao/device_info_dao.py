from base import db
from base.com.vo.device_info_vo import DeviceInfoVO


class DeviceInfoDAO:
    def insert_device_info(self, device_info_vo):
        db.session.add(device_info_vo)
        db.session.commit()

    def search_device(self, login_vo):
        return DeviceInfoVO.query. \
            filter_by(device_login_id=login_vo.login_id).all()

    def delete_all_device(self, login_id):
        device_list = DeviceInfoVO.query. \
            filter_by(device_login_id=login_id).all()
        for device_vo in device_list:
            db.session.delete(device_vo)
            db.session.commit()

    def delete_device(self, device_vo):
        device_info_vo = DeviceInfoVO.query.get(device_vo.device_id)
        db.session.delete(device_info_vo)
        db.session.commit()
