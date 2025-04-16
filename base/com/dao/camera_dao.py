from base import db
from base.com.vo.area_vo import AreaVO
from base.com.vo.camera_vo import CameraVO
from base.com.vo.crossroad_vo import CrossroadVO


class CameraDAO:
    def insert_camera(self, camera_vo):
        db.session.add(camera_vo)
        db.session.commit()

    def delete_camera(self, camera_vo):
        camera_vo = CameraVO.query.get(camera_vo.camera_id)
        db.session.delete(camera_vo)
        db.session.commit()

    def edit_camera(self, camera_vo):
        camera_vo_list = CameraVO.query.filter_by(
            camera_id=camera_vo.camera_id).all()
        print('camera_vo_list.........>>>>>>>>>>', camera_vo_list)
        return camera_vo_list

    def update_camera(self, camera_vo):
        db.session.merge(camera_vo)
        db.session.commit()

    def view_camera(self):
        camera_vo_list = db.session.query(AreaVO, CrossroadVO,
                                          CameraVO) \
            .filter(AreaVO.area_id == CameraVO.camera_area_id) \
            .filter(
            CrossroadVO.crossroad_id == CameraVO.camera_crossroad_id) \
            .all()
        return camera_vo_list

    def view_ajax_camera(self, camera_vo):
        camera_vo_list = CameraVO.query.filter_by(
            camera_crossroad_id=camera_vo.camera_crossroad_id).all()
        print(">>>>>>>>>>", camera_vo_list)
        return camera_vo_list
