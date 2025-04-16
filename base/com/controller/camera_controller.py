from flask import request, render_template, redirect, jsonify

from base import app
from base.com.controller.login_controller import login_required
from base.com.dao.area_dao import AreaDAO
from base.com.dao.camera_dao import CameraDAO
from base.com.dao.crossroad_dao import CrossroadDAO
from base.com.vo.camera_vo import CameraVO
from base.com.vo.crossroad_vo import CrossroadVO


@app.route('/add_camera')
@login_required('admin')
def add_camera():
    area_dao = AreaDAO()
    area_vo_list = area_dao.view_area()
    return render_template('admin/addCamera.html',
                           area_vo_list=area_vo_list)


@app.route('/ajax_crossroad_camera')
def ajax_crossroad_camera():
    crossroad_vo = CrossroadVO()
    crossroad_dao = CrossroadDAO()

    crossroad_area_id = request.args.get('camera_area_id')
    crossroad_vo.crossroad_area_id = crossroad_area_id
    crossroad_vo_list = crossroad_dao.view_ajax_crossroad_camera(crossroad_vo)
    ajax_camera_crossroad = [crossroad_vo_list.as_dict() for crossroad_vo_list
                             in
                             crossroad_vo_list]
    print(crossroad_vo_list)
    return jsonify(ajax_camera_crossroad)


@app.route('/insert_camera', methods=['POST'])
@login_required('admin')
def insert_camera():
    camera_area_id = request.form.get('camera_area_id')
    camera_crossroad_id = request.form.get('camera_crossroad_id')
    camera_name = request.form.get('camera_name')
    camera_code = request.form.get('camera_code')
    camera_link = request.form.get('camera_link')

    camera_vo = CameraVO()
    camera_dao = CameraDAO()

    camera_vo.camera_name = camera_name
    camera_vo.camera_code = camera_code
    camera_vo.camera_link = camera_link
    camera_vo.camera_area_id = camera_area_id
    camera_vo.camera_crossroad_id = camera_crossroad_id
    camera_dao.insert_camera(camera_vo)
    return redirect('/view_camera')


@app.route('/delete_camera')
@login_required('admin')
def delete_camera():
    camera_dao = CameraDAO()
    camera_vo = CameraVO()

    camera_id = request.args.get('camera_id')
    camera_vo.camera_id = camera_id
    camera_dao.delete_camera(camera_vo)

    return redirect('/view_camera')


@app.route('/edit_camera')
@login_required('admin')
def edit_camera():
    area_dao = AreaDAO()
    crossroad_dao = CrossroadDAO()
    crossroad_vo = CrossroadVO()
    camera_vo = CameraVO()
    camera_dao = CameraDAO()

    camera_id = request.args.get('camera_id')
    camera_vo.camera_id = camera_id
    camera_vo_list = camera_dao.edit_camera(camera_vo)

    camera_vo_dict = camera_vo_list[0].as_dict()
    # print(">>>>>>>>>>>", camera_vo_dict)

    camera_area_id = camera_vo_dict.get('camera_area_id')
    crossroad_vo.crossroad_area_id = camera_area_id

    crossroad_vo_list = crossroad_dao.view_ajax_crossroad_camera(crossroad_vo)
    area_vo_list = area_dao.view_area()

    # print('area_vo_list>>>>>>>>', area_vo_list)
    # print('crossroad_vo_list>>>>>>>>', crossroad_vo_list)
    # print('camera_vo_list>>>>>>>>', camera_vo_list)
    return render_template('admin/editCamera.html',
                           camera_vo_list=camera_vo_list,
                           area_vo_list=area_vo_list,
                           crossroad_vo_list=crossroad_vo_list)


@app.route('/update_camera', methods=['POST'])
@login_required('admin')
def update_camera():
    camera_id = request.form.get('camera_id')
    camera_name = request.form.get('camera_name')
    camera_code = request.form.get('camera_code')
    camera_link = request.form.get('camera_link')
    camera_area_id = request.form.get('camera_area_id')
    camera_crossroad_id = request.form.get('camera_crossroad_id')

    camera_dao = CameraDAO()
    camera_vo = CameraVO()

    camera_vo.camera_id = camera_id
    camera_vo.camera_name = camera_name
    camera_vo.camera_code = camera_code
    camera_vo.camera_link = camera_link
    camera_vo.camera_area_id = camera_area_id
    camera_vo.camera_crossroad_id = camera_crossroad_id
    # print('camera_vo.camera_id>>>>>>>>.......', camera_vo)
    camera_dao.update_camera(camera_vo)
    return redirect('/view_camera')


@app.route('/view_camera')
@login_required('admin')
def view_camera():
    camera_dao = CameraDAO()
    camera_vo_list = camera_dao.view_camera()
    return render_template('admin/viewcamera.html',
                           camera_vo_list=camera_vo_list)
