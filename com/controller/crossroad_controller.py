from flask import render_template, request, redirect

from base import app
from base.com.controller.login_controller import login_required
# from base.com.vo.area_vo import AreaVO
from base.com.dao.area_dao import AreaDAO
from base.com.dao.crossroad_dao import CrossroadDAO
from base.com.vo.crossroad_vo import CrossroadVO


@app.route('/add_crossroad')
@login_required('admin')
def load_crossroad():
    area_dao = AreaDAO()
    area_vo_list = area_dao.view_area()
    return render_template('admin/addCrossroad.html',
                           area_vo_list=area_vo_list)


@app.route('/insert_crossroad', methods=['POST'])
@login_required('admin')
def insert_crossroad():
    crossroad_area_id = request.form.get('crossroad_area_id')
    crossroad_name = request.form.get('crossroad_name')
    crossroad_description = request.form.get('crossroad_description')

    crossroad_dao = CrossroadDAO()
    crossroad_vo = CrossroadVO()

    crossroad_vo.crossroad_name = crossroad_name
    crossroad_vo.crossroad_description = crossroad_description
    crossroad_vo.crossroad_area_id = crossroad_area_id
    print(crossroad_vo)

    crossroad_dao.insert_crossroad(crossroad_vo)

    return redirect('/view_crossroad')


@app.route('/delete_crossroad')
@login_required('admin')
def delete_crossroad():
    crossroad_id = request.args.get('crossroad_id')
    crossroad_vo = CrossroadVO()
    crossroad_vo.crossroad_id = crossroad_id
    crossroad_dao = CrossroadDAO()
    crossroad_dao.delete_crossroad(crossroad_vo)
    return redirect('/view_crossroad')


@app.route('/edit_crossroad')
@login_required('admin')
def edit_crossroad():
    crossroad_vo = CrossroadVO()
    area_dao = AreaDAO()
    crossroad_dao = CrossroadDAO()

    crossroad_id = request.args.get('crossroad_id')
    print(">>>>>>>>", crossroad_id)
    crossroad_vo.crossroad_id = crossroad_id
    crossroad_vo_list = crossroad_dao.edit_crossroad(crossroad_vo)
    area_vo_list = area_dao.view_area()
    return render_template('admin/editCrossroad.html',
                           area_vo_list=area_vo_list,
                           crossroad_vo_list=crossroad_vo_list)


@app.route('/update_crossroad', methods=['POST'])
@login_required('admin')
def update_crossroad():
    crossroad_vo = CrossroadVO()
    crossroad_dao = CrossroadDAO()

    crossroad_id = request.form.get('crossroad_id')
    # print("????????",crossroad_id)
    crossroad_area_id = request.form.get("crossroad_area_id")
    print("+++++++", crossroad_area_id)
    crossroad_name = request.form.get("crossroad_name")
    crossroad_description = request.form.get("crossroad_description")

    crossroad_vo.crossroad_id = crossroad_id
    crossroad_vo.crossroad_area_id = crossroad_area_id
    crossroad_vo.crossroad_name = crossroad_name
    crossroad_vo.crossroad_description = crossroad_description
    # print("subcategory_vo>>>>>>>>>>>>>>>>>>>>",crossroad_vo)

    crossroad_dao.update_crossroad(crossroad_vo)

    return redirect("/view_crossroad")


@app.route('/view_crossroad')
@login_required('admin')
def view_crossroad():
    crossroad_dao = CrossroadDAO()
    crossroad_vo_list = crossroad_dao.view_crossroad()
    print("crossroad_vo_list=", crossroad_vo_list)
    return render_template('admin/viewCrossroad.html',
                           crossroad_vo_list=crossroad_vo_list)
