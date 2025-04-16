from base import db
from base.com.vo.area_vo import AreaVO
from base.com.vo.crossroad_vo import CrossroadVO


class CameraVO(db.Model):
    __tablename__ = 'camera_table'

    camera_id = db.Column('camera_id', db.Integer, primary_key=True,
                          autoincrement=True)

    camera_name = db.Column('camera_name', db.String(255), nullable=False)

    camera_code = db.Column('camera_code', db.Integer, nullable=False)

    camera_link = db.Column('camera_link', db.String(255), nullable=False)

    camera_area_id = db.Column('camera_area_id', db.Integer,
                               db.ForeignKey(AreaVO.area_id,
                                             ondelete='CASCADE',
                                             onupdate='CASCADE'))

    camera_crossroad_id = db.Column('camera_crossroad_id', db.Integer,
                                    db.ForeignKey(CrossroadVO.crossroad_id,
                                                  ondelete='CASCADE',
                                                  onupdate='CASCADE'))

    def as_dict(self):
        return {
            'camera_id': self.camera_id,
            'camera_name': self.camera_name,
            'camera_code': self.camera_code,
            'camera_link': self.camera_link,
            'camera_area_id': self.camera_area_id,
            'camera_crossroad_id': self.camera_crossroad_id,

        }


db.create_all()
