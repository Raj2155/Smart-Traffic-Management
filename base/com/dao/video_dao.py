from base import db
from base.com.vo.area_vo import AreaVO
from base.com.vo.camera_vo import CameraVO
from base.com.vo.crossroad_vo import CrossroadVO
from base.com.vo.video_vo import VideoVO


class VideoDAO:
    def insert_video(self, video_vo):
        db.session.add(video_vo)
        db.session.commit()

    # def view_video(self):
    #     video_vo_list = VideoVO.query.all()
    #     return video_vo_list

    def view_video(self):
        video_vo_list = db.session.query(AreaVO, CrossroadVO,
                                         CameraVO, VideoVO) \
            .filter(AreaVO.area_id == VideoVO.video_area_id) \
            .filter(
            CrossroadVO.crossroad_id == VideoVO.video_crossroad_id).filter(
            CameraVO.camera_id == VideoVO.video_camera_id).all()

        return video_vo_list

    def total_count(self):
        video_vo_list = VideoVO.query.all()
        return video_vo_list

    def delete_history(self, video_vo):
        video_vo_list = VideoVO.query.get(video_vo.video_id)
        db.session.delete(video_vo_list)
        print("video_vo_list+++++++++++", video_vo_list)
        db.session.commit()
        return video_vo_list
