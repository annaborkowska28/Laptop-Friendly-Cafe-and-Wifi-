from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_bootstrap import Bootstrap5
import os
from dotenv import load_dotenv


app = Flask(__name__)
bootstrap = Bootstrap5(app)


class Base(DeclarativeBase):
    pass
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SECRET_KEY'] = os.getenv('secret_key')
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# with app.app_context():
#     db.create_all()


@app.route("/")
def home():
    all_cafes = Cafe.query.order_by(Cafe.id).all()
    recent_cafes = Cafe.query.order_by(Cafe.id.desc()).limit(3).all()
    for i, cafe in enumerate(all_cafes):
        cafe.ranking = len(all_cafes) - i


    return render_template("index.html", all_cafes=all_cafes, recent_cafes=recent_cafes)



@app.route('/search')
def search():
    location = request.args.get('location', '').strip().lower()
    if not location:
        return redirect(url_for('home'))
    cafes = Cafe.query.filter(Cafe.location.ilike(f'%{location}%')).all()
    return render_template('search.html', cafes=cafes, location=location)


#------------------------- ADD NEW CAFE ----------------------------------------
@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    if request.method == 'POST':
        cafe_name = request.form['name']
        map_url = request.form['map_url']
        img_url = request.form['img_url']
        location = request.form['location']
        has_sockets = int(request.form['has_sockets'])
        has_toilet = int(request.form['has_toilet'])
        has_wifi = int(request.form['has_wifi'])
        can_take_calls = int(request.form['can_take_calls'])
        seats = request.form['seats']
        coffee_price = request.form['coffee_price']
        new_cafe = Cafe(name=cafe_name,
                        map_url=map_url,
                        img_url=img_url,
                        location=location,
                        has_sockets=has_sockets,
                        has_toilet=has_toilet,
                        has_wifi=has_wifi,
                        can_take_calls=can_take_calls,
                        seats=seats,
                        coffee_price=coffee_price)
        db.session.add(new_cafe)
        db.session.commit()
        db.session.close_all()
        flash("Successfully added new café!", "success")
        return redirect(url_for("add_cafe"))
    return render_template("add.html")



@app.route('/edit', methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        try:
            cafe_id = request.form['id']
            cafe_to_update = db.get_or_404(Cafe, cafe_id)
            cafe_to_update.name = request.form['name']
            cafe_to_update.map_url = request.form['map_url']
            cafe_to_update.img_url = request.form['img_url']
            cafe_to_update.location = request.form['location']
            cafe_to_update.has_sockets = int(request.form['has_sockets'])
            cafe_to_update.has_toilet = int(request.form['has_toilet'])
            cafe_to_update.has_wifi = int(request.form['has_wifi'])
            cafe_to_update.can_take_calls = int(request.form['can_take_calls'])
            cafe_to_update.seats = request.form['seats']
            cafe_to_update.coffee_price = request.form['coffee_price']
            db.session.commit()
            return redirect(url_for('home'))
        except KeyError as e:
            flash(f"Missing form field: {e}")
            return redirect(url_for('edit', id=request.form['id']))
    cafe_id = request.args.get('id')
    cafe_selected = db.get_or_404(Cafe, cafe_id)

    return render_template('edit.html', cafe=cafe_selected)


@app.route('/delete')
def delete():
    cafe_id = request.args.get('id')
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    flash("Successfully deleted!", "success")

    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html', is_about=True)

if __name__ == '__main__':
    app.run(debug=True)