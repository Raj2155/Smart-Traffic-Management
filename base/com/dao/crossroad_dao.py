from base import db
from base.com.vo.area_vo import AreaVO
from base.com.vo.crossroad_vo import CrossroadVO


class CrossroadDAO:
    def insert_crossroad(self, crossroad_vo):
        db.session.add(crossroad_vo)
        db.session.commit()

    def view_crossroad(self):
        crossroad_vo_list = db.session.query(CrossroadVO, AreaVO) \
            .join(AreaVO,
                  CrossroadVO.crossroad_area_id == AreaVO.area_id).all()
        return crossroad_vo_list

    def delete_crossroad(self, crossroad_vo):
        crossroad_vo = CrossroadVO.query.get(crossroad_vo.crossroad_id)
        db.session.delete(crossroad_vo)
        db.session.commit()

    def edit_crossroad(self, crossroad_vo):
        crossroad_vo_list = CrossroadVO.query.filter_by(
            crossroad_id=crossroad_vo.crossroad_id).all()
        return crossroad_vo_list

    def update_crossroad(self, crossroad_vo):
        db.session.merge(crossroad_vo)
        db.session.commit()

    def view_ajax_crossroad_camera(self, crossroad_vo):
        crossroad_vo_list = CrossroadVO.query.filter_by(
            crossroad_area_id=crossroad_vo.crossroad_area_id).all()
        print(">>>>>>>>>>", crossroad_vo_list)
        return crossroad_vo_list
