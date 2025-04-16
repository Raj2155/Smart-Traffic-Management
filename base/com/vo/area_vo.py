from base import db


class AreaVO(db.Model):
    __tablename__ = 'area_table'

    area_id = db.Column('area_id', db.Integer, primary_key=True,
                        autoincrement=True)

    area_name = db.Column('area_name', db.String(255), nullable=False)

    area_code = db.Column('area_code', db.Integer, nullable=False)

    def as_dict(self):
        return {
            'area_id': self.area_id,
            'area_name': self.area_name,
            'area_code': self.area_code,

        }


db.create_all()
