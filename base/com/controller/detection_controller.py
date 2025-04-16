import os
from datetime import datetime

from flask import render_template, request, redirect, jsonify
from werkzeug.utils import secure_filename

from base import app
from base.com.controller.login_controller import login_required
from base.com.dao.area_dao import AreaDAO
from base.com.dao.camera_dao import CameraDAO
from base.com.dao.crossroad_dao import CrossroadDAO
from base.com.dao.video_dao import VideoDAO
from base.com.vo.camera_vo import CameraVO
from base.com.vo.crossroad_vo import CrossroadVO
from base.com.vo.video_vo import VideoVO
from base.services.multi_updown_obj_det_and_trk import detect

INPUT_FOLDER = 'base/static/adminResources/input_video'
app.config['INPUT_FOLDER'] = INPUT_FOLDER

OUTPUT_FOLDER = 'base/static/adminResources/output_video'
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


# @app.route('/home_load')
# def home():
#         return render_template('admin/index.html')


# @app.route('/upload_video')
# def upload_video():
#     return render_template('admin/addVideo.html')

@app.route('/upload_video')
@login_required('admin')
def select_area():
    area_dao = AreaDAO()
    area_vo_list = area_dao.view_area()
    return render_template('admin/addVideo.html',
                           area_vo_list=area_vo_list)


@app.route('/detect_video', methods=['POST'])
@login_required('admin')
def detect_video():
    # try:

    input_video = request.files.get("input_video")
    video_name = secure_filename(input_video.filename)

    input_video_path = os.path.join(app.config['INPUT_FOLDER'])
    input_video.save(os.path.join(input_video_path, video_name))
    detect_video = input_video_path + "/" + video_name

    output_path, total_entry_count, total_exit_count = detect(
        source=detect_video)

    # timer logic
    time_diff = ""
    count_diff = abs(total_entry_count - total_exit_count)
    if count_diff == 0:
        time_diff = "10 secs"
    elif 0 < count_diff <= 15:
        time_diff = "20 secs"
    elif 16 < count_diff <= 30:
        time_diff = "40 secs"
    elif 31 < count_diff <= 45:
        time_diff = "60 secs"
    elif 46 < count_diff <= 60:
        time_diff = "80 secs"
    elif 61 < count_diff <= 75:
        time_diff = "100 secs"
    else:
        time_diff = "120 secs"

    video_dao = VideoDAO()
    video_vo = VideoVO()
    area_name = request.form.get('crossroad_area_id')
    crossroad_name = request.form.get('camera_crossroad_id')
    camera_name = request.form.get('camera_id')
    video_vo.video_camera_id = camera_name
    video_vo.video_area_id = area_name
    video_vo.video_crossroad_id = crossroad_name

    current_date = datetime.now()
    video_vo.video_datetime = current_date
    video_vo.input_video = detect_video.replace("base", "..")
    video_vo.output_video = output_path.replace("base", "..")
    video_vo.entry_count = total_entry_count
    video_vo.exit_count = total_exit_count
    video_vo.time_diff = time_diff

    video_dao.insert_video(video_vo)

    return render_template("admin/addVideo.html")


@app.route('/view_history')
@login_required('admin')
def view_history():
    video_dao = VideoDAO()
    video_vo_list = video_dao.view_video()
    return render_template('admin/history.html', video_vo_list=video_vo_list)


# @app.route('/about')
# def about():
#         return render_template('admin/about.html')

@app.route('/delete_video')
@login_required('admin')
def delete_video():
    video_dao = VideoDAO()
    video_vo = VideoVO()
    video_id = request.args.get('videoId')
    video_vo.video_id = video_id
    video_vo_list = video_dao.delete_history(video_vo)
    # file_path = (video_vo_list.input_video.replace("..","base") + video_vo_list.input_video)
    file_path = video_vo_list.input_video.replace("..", "base")
    os.remove(file_path)
    # output_file_path = (video_vo_list.output_video.replace("..","base")+video_vo_list.output_video)
    output_file_path = video_vo_list.output_video.replace("..", "base")
    os.remove(output_file_path)

    return redirect("/view_history")


@app.route('/ajax_select_crossroad')
@login_required('admin')
def ajax_select_crossroad():
    crossroad_vo = CrossroadVO()
    crossroad_dao = CrossroadDAO()

    crossroad_area_id = request.args.get('crossroad_area_id')
    crossroad_vo.crossroad_area_id = crossroad_area_id
    crossroad_vo_list = crossroad_dao.view_ajax_crossroad_camera(crossroad_vo)
    ajax_camera_crossroad = [crossroad_vo_list.as_dict() for crossroad_vo_list
                             in
                             crossroad_vo_list]
    print(crossroad_vo_list)
    return jsonify(ajax_camera_crossroad)


@app.route('/ajax_select_camera')
@login_required('admin')
def ajax_select_camera():
    area_dao = AreaDAO()
    crossroad_dao = CrossroadDAO()
    crossroad_vo = CrossroadVO()
    camera_vo = CameraVO()
    camera_dao = CameraDAO()

    camera_crossroad_id = request.args.get('crossroad_id')
    camera_vo.camera_crossroad_id = camera_crossroad_id
    camera_vo_list = camera_dao.view_ajax_camera(camera_vo)
    ajax_camera_crossroad = [camera_vo_list.as_dict() for camera_vo_list
                             in
                             camera_vo_list]
    print(camera_vo_list)
    return jsonify(ajax_camera_crossroad)
