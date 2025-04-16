from base import db
from base.com.vo.login_vo import LoginVO


class DeviceInfoVO(db.Model):
    __tablename__ = 'device_info_table'
    device_id = db.Column('device_id', db.Integer, primary_key=True,
                          autoincrement=True)
    device_identity = db.Column('device_identity', db.String(250),
                                nullable=False)

    device_login_id = db.Column('device_login_id', db.Integer,
                                db.ForeignKey(LoginVO.login_id,
                                              ondelete='CASCADE',
                                              onupdate='CASCADE'),
                                nullable=False)

    def as_dict(self):
        return {
            'device_id': self.device_id,
            'device_identity ': self.device_identity,
            'device_login_id': self.device_login_id,
        }


db.create_all()
