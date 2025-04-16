from flask import render_template, request, redirect

from base import app
from base.com.controller.login_controller import login_required
from base.com.dao.area_dao import AreaDAO
from base.com.vo.area_vo import AreaVO


@app.route('/add_area')
@login_required('admin')
def add_area():
    return render_template('admin/addArea.html')


@app.route('/insert_area', methods=['POST'])
@login_required('admin')
def insert_Area():
    area_name = request.form.get('area_name')
    area_code = request.form.get('area_code')

    area_vo = AreaVO()
    area_dao = AreaDAO()

    area_vo.area_name = area_name
    area_vo.area_code = area_code

    area_dao.add_area(area_vo)

    return redirect('/view_area')


@app.route('/view_area')
@login_required('admin')
def view_area():
    area_dao = AreaDAO()
    area_vo_list = area_dao.view_area()
    print("area_vo_list=", area_vo_list)
    return render_template('admin/viewArea.html',
                           area_vo_list=area_vo_list)


@app.route('/delete_area')
def delete_area():
    area_id = request.args.get('area_id')
    area_vo = AreaVO()
    area_vo.area_id = area_id
    area_dao = AreaDAO()
    area_dao.delete_area(area_vo)
    return redirect('/view_area')


@app.route('/edit_area')
def edit_area():
    area_vo = AreaVO()
    area_dao = AreaDAO()

    area_id = request.args.get('area_id')
    area_vo.area_id = area_id
    area_vo_list = area_dao.edit_area(area_vo)

    return render_template('admin/editArea.html', area_vo_list=area_vo_list)


@app.route('/update_area', methods=['POST'])
def update_area():
    area_vo = AreaVO()
    area_dao = AreaDAO()

    area_id = request.form.get('area_id')

    area_name = request.form.get("area_name")
    area_code = request.form.get("area_code")

    area_vo.area_id = area_id
    area_vo.area_name = area_name
    area_vo.area_code = area_code

    area_dao.update_area(area_vo)

    return redirect("/view_area")
