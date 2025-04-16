from base import db
from base.com.vo.area_vo import AreaVO
from base.com.vo.camera_vo import CameraVO
from base.com.vo.crossroad_vo import CrossroadVO


class VideoVO(db.Model):
    __tablename__ = 'video_table'

    video_id = db.Column('video_id', db.Integer, primary_key=True,
                         autoincrement=True)
    video_datetime = db.Column('video_datetime', db.DATETIME(), nullable=True)
    input_video = db.Column('input_video', db.String(255),
                            nullable=True)
    output_video = db.Column('output_video', db.String(255),
                             nullable=True)
    time_diff = db.Column('time_diff', db.String(255),
                          nullable=True)
    entry_count = db.Column('entry_count', db.Integer,
                            nullable=True)
    exit_count = db.Column('exit_count', db.Integer,
                           nullable=True)
    video_area_id = db.Column('video_area_id', db.Integer,
                              db.ForeignKey(AreaVO.area_id, ))

    video_crossroad_id = db.Column('video_crossroad_id', db.Integer,
                                   db.ForeignKey(CrossroadVO.crossroad_id, ))
    video_camera_id = db.Column('video_camera_id', db.Integer,
                                db.ForeignKey(CameraVO.camera_id, ))

    def as_dict(self):
        return {
            'video_id': self.video_id,
            'video_datetime': self.video_datetime,
            'input_video': self.input_video,
            'output_video': self.output_video,
            'time_diff': self.time_diff,
            'entry_count': self.entry_count,
            'exit_count': self.exit_count,
            'video_area_id': self.video_area_id,
            'video_crossroad_id': self.video_crossroad_id,
            'video_camera_id': self.video_camera_id,
        }


db.create_all()
