from flask import flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy import or_

from app.core.dates import local_today
from app.core.files import UploadError, access_rule, accept_attribute, delete_stored, save_upload
from app.core.security import admin_required
from app.extensions import db
from app.models import CampusMap, Room, ScheduleEntry
from app.models.schedule import entries_for_day

from . import bp
from .forms import KIND_LABELS, MapForm, RoomForm


@access_rule("campus")
def _can_download_map(user, stored):
    return True  # plans visibles par tous les membres connectés


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    kind = request.args.get("type", "")
    query = Room.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Room.name.ilike(like), Room.code.ilike(like), Room.building.ilike(like)))
    if kind in KIND_LABELS:
        query = query.filter(Room.kind == kind)
    rooms = query.order_by(Room.kind, Room.name).all()
    maps = CampusMap.query.order_by(CampusMap.position, CampusMap.title).all()
    return render_template("campus/index.html", rooms=rooms, maps=maps, q=q, kind=kind, kinds=KIND_LABELS)


@bp.route("/salles/<int:room_id>")
@login_required
def show(room_id):
    room = db.get_or_404(Room, room_id)
    today = local_today()
    sessions = [e for e in entries_for_day(today) if e.room_id == room.id]
    return render_template("campus/show.html", room=room, kinds=KIND_LABELS, sessions=sessions, today=today)


# --- Gestion (administration) ---------------------------------------------

@bp.route("/gestion", methods=["GET", "POST"])
@admin_required
def manage():
    form = MapForm()
    if form.validate_on_submit():
        try:
            stored = save_upload(form.image.data, "campus", current_user.id)
        except UploadError as err:
            form.image.errors.append(str(err))
        else:
            db.session.add(CampusMap(title=form.title.data, file=stored, position=CampusMap.query.count()))
            db.session.commit()
            flash(_("Plan ajouté."), "success")
            return redirect(url_for("campus.manage"))
    rooms = Room.query.order_by(Room.name).all()
    maps = CampusMap.query.order_by(CampusMap.position).all()
    return render_template("campus/manage.html", rooms=rooms, maps=maps, form=form, kinds=KIND_LABELS,
                           accept=accept_attribute("campus"), csrf_form=FlaskForm())


@bp.route("/gestion/plans/<int:map_id>/supprimer", methods=["POST"])
@admin_required
def delete_map(map_id):
    campus_map = db.get_or_404(CampusMap, map_id)
    stored = campus_map.file
    db.session.delete(campus_map)
    delete_stored(stored)
    db.session.commit()
    flash(_("Plan supprimé."), "success")
    return redirect(url_for("campus.manage"))


@bp.route("/gestion/salles/nouvelle", methods=["GET", "POST"], defaults={"room_id": None})
@bp.route("/gestion/salles/<int:room_id>", methods=["GET", "POST"])
@admin_required
def edit(room_id):
    room = db.get_or_404(Room, room_id) if room_id else None
    form = RoomForm(obj=room)
    if form.validate_on_submit():
        duplicate = Room.query.filter(Room.code == form.code.data)
        if room:
            duplicate = duplicate.filter(Room.id != room.id)
        if duplicate.first():
            form.code.errors.append(_("Ce code est déjà utilisé."))
        elif (form.latitude.data is None) != (form.longitude.data is None):
            form.longitude.errors.append(_("Renseignez la latitude et la longitude, ou aucune des deux."))
        else:
            if room is None:
                room = Room()
                db.session.add(room)
            form.populate_obj(room)
            db.session.commit()
            flash(_("Lieu enregistré."), "success")
            return redirect(url_for("campus.show", room_id=room.id))
    return render_template("campus/edit.html", form=form, room=room)


@bp.route("/gestion/salles/<int:room_id>/supprimer", methods=["POST"])
@admin_required
def delete(room_id):
    room = db.get_or_404(Room, room_id)
    ScheduleEntry.query.filter_by(room_id=room.id).update({"room_id": None})
    db.session.delete(room)
    db.session.commit()
    flash(_("Lieu supprimé. Les séances qui l'utilisaient n'ont plus de salle."), "success")
    return redirect(url_for("campus.manage"))
