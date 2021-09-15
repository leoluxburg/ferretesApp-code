from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, make_response, Response
import os
from . import db
from .models import Iron
from .models import User
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
import pdfkit
import numpy as np
from PIL import Image
from .feature_extractor import FeatureExtractor
from datetime import datetime
from pathlib import Path


main = Blueprint('main', __name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT2 = os.path.dirname(os.path.abspath(__file__))


fe = FeatureExtractor()
features = []
img_paths = []
for feature_path in Path("project/static/feature").glob("*.npy"):
    features.append(np.load(feature_path))
    img_paths.append(Path("/static/f-images") / (feature_path.stem + ".jpg"))
features = np.array(features)

@main.route("/filter", methods = ["GET", "POST"])
def filter():
  if request.method == "POST":
    file = request.files["query_img"]

    # Save query image
    img = Image.open(file.stream)  # PIL image
    uploaded_img_path = "project/static/uploaded/" + datetime.now().isoformat().replace(":", ".") + "_" + file.filename
    img.save(uploaded_img_path)

    image_f = "static/uploaded/" + datetime.now().isoformat().replace(":", ".") + "_" + file.filename
    img_f = str(image_f)
    # Run search
    query = fe.extract(img)
    dists = np.linalg.norm(features-query, axis=1)  # L2 distances to features
    ids = np.argsort(dists)[:30]  # Top 30 results
    scores = [(dists[id], img_paths[id]) for id in ids]

    return render_template("filter.html", query_path=uploaded_img_path, scores=scores, image_f = img_f)
  else:
    return render_template("filter.html")

@main.route('/dsng')
def dsgn():
  q = request.args.get('q')

  if q:
    irons = Iron.query.filter(Iron.nombre.contains(q))

  else:
    irons = Iron.query.all()

  return render_template('irons.html', irons = irons)


@main.route('/')
def index():
    q = request.args.get('q')

    if q:
        irons = Iron.query.filter(Iron.nombre.contains(q))

    else:
      irons = Iron.query.all()

    return render_template('irons.html', irons = irons )

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/new')
@login_required
def new_iron():
  return render_template('create_iron.html')

@main.route('/search')
def search():
  return render_template('irons.html')

@main.route('/new', methods = ['POST'])
@login_required
def new_iron_post():

  nombre = request.form.get('nombre')
  cedula = request.form.get('cedula')
  domicilio = request.form.get('domicilio')
  correo = request.form.get('correo')
  telefono = request.form.get('telefono')

  iron = Iron(nombre = nombre, cedula = cedula, domicilio = domicilio,  user_id = current_user.id, correo = correo, telefono = telefono, )

  db.session.add(iron)
  db.session.commit()

  target = os.path.join(APP_ROOT, 'static/ferretes')


  if not os.path.isdir(target):
    os.mkdir(target)
  else:
    print("Couldn't create directory ferretes".format(target))

  print('check')

  for file in request.files.getlist("file"):
    print('debug1')
    print(file.filename)
    filename = file.filename
    a = "ferrete"
    b = ".jpg"
    c =  str(iron.id)
    file_name = "ferrete\'%s\'.jpg"%(int(iron.id))
    file_name2 = a + c + b
    destination = "/".join([target, file_name2])
    print(destination)
    file.save(destination)


  target2 = os.path.join(APP_ROOT, 'static/cedulas')

  if not os.path.isdir(target2):
    os.mkdir(target2)
  else:
    print("Couldn't create directory cedulas".format(target2))


  for cedula_img in request.files.getlist("cedula_img"):
    print('debug2')
    print(cedula_img.filename)
    filename = cedula_img.filename
    a = "cedula"
    b = ".jpg"
    c =  str(iron.id)
    file_name = "ferrete\'%s\'.jpg"%(int(iron.id))
    file_name2 = a + c + b
    destination = "/".join([target2, file_name2])
    print(destination)
    cedula_img.save(destination)


  return redirect(url_for('main.irons'))


@main.route('/irons')
def irons():
  q = request.args.get('q')

  if q:
    irons = Iron.query.filter(Iron.nombre.contains(q))

  else:
    irons = Iron.query.all()

  return render_template('irons.html', irons = irons )


@main.route("/irons/<int:iron_id>/update", methods=['GET', 'POST'])
@login_required
def update_iron(iron_id):
    iron = Iron.query.get_or_404(iron_id)
    if request.method == "POST":
        iron.nombre = request.form['nombre']
        iron.cedula = request.form['cedula']
        iron.domicilio = request.form['domicilio']

        db.session.commit()
        flash('Your post has been updated!')
        return redirect(url_for('main.irons'))

    return render_template('update_iron.html', iron=iron)


@main.route("/irons/<int:iron_id>", methods=['GET'])
@login_required
def show_iron(iron_id):
    iron = Iron.query.get_or_404(iron_id)
    if request.method == "POST":
        iron.nombre = request.form['nombre']
        iron.cedula = request.form['cedula']
        iron.domicilio = request.form['domicilio']


    url = request.base_url
    qr_url = "{{qrcode(\'%s\')}}"%(url)

    converted_id = str(iron.id)
    x = "/static/ferretes/ferrete" + converted_id +".jpg"
    y = "/static/cedulas/cedula" + converted_id +".jpg"


    return render_template('iron.html', iron=iron, qr = qr_url, url = url, img = x, cedula = y)


@main.route("/irons/<int:iron_id>/pdf", methods=['GET'])
@login_required
def pdf_iron(iron_id):
    iron = Iron.query.get_or_404(iron_id)
    url = request.base_url

    render = render_template('pdf-doc.html', iron=iron, url = url)
    pdf = pdfkit.from_string(render, False)

    url = request.base_url
    qr_url = "{{qrcode(\'%s\')}}"%(url)

    print(url)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Dis['] = 'application/pdf'

    return response


@main.route('/irons/<int:iron_id>/img')
def get_img(iron_id):
    iron = Iron.query.filter_by(id=iron_id).first()
    if not iron:
        return 'Img Not Found!', 404

    return Response(iron.img, mimetype=iron.mimetype)

@main.route('/act')
def act():
  print ("Running")
  exec(open("project/offline.py").read())
  return render_template('act.html')



