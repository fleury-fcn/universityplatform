from flask import flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from app.core.security import admin_required
from app.extensions import db
from app.main.widgets import home_widget
from app.models import News, NewsCategory, Promotion, utcnow
from app.services.notifications import mark_read, notify, recipients

from . import bp
from .forms import CategoryForm, NewsForm

PER_PAGE = 15


def _ordered(query):
    return query.order_by(News.is_pinned.desc(), News.published_at.desc())


@home_widget(order=20)
def latest_news_widget(user):
    items = _ordered(News.visible_to(user)).limit(3).all()
    return ("news/_widget.html", {"items": items}) if items else None


@bp.route("/")
@login_required
def index():
    category_id = request.args.get("categorie", type=int)
    query = News.visible_to(current_user)
    if category_id:
        query = query.filter(News.category_id == category_id)
    page = _ordered(query).paginate(per_page=PER_PAGE, error_out=False)
    categories = NewsCategory.query.order_by(NewsCategory.position, NewsCategory.name).all()
    return render_template("news/index.html", page=page, categories=categories, category_id=category_id)


@bp.route("/<int:news_id>")
@login_required
def show(news_id):
    item = News.visible_to(current_user).filter(News.id == news_id).first_or_404()
    mark_read(current_user.id, url=url_for("news.show", news_id=item.id))
    db.session.commit()
    return render_template("news/show.html", item=item)


# --- Gestion (administration) ---------------------------------------------

@bp.route("/gestion", methods=["GET", "POST"])
@admin_required
def manage():
    category_form = CategoryForm()
    if category_form.validate_on_submit():
        if NewsCategory.query.filter_by(name=category_form.name.data).first():
            flash(_("Cette catégorie existe déjà."), "warning")
        else:
            db.session.add(NewsCategory(name=category_form.name.data, position=NewsCategory.query.count()))
            db.session.commit()
            flash(_("Catégorie ajoutée."), "success")
        return redirect(url_for("news.manage"))
    page = News.query.order_by(News.created_at.desc()).paginate(per_page=PER_PAGE, error_out=False)
    categories = NewsCategory.query.order_by(NewsCategory.position).all()
    return render_template("news/manage.html", page=page, categories=categories, category_form=category_form)


def _form_choices(form):
    form.category_id.choices = [(0, _("Sans catégorie"))] + [
        (c.id, c.name) for c in NewsCategory.query.order_by(NewsCategory.position)
    ]
    form.promotion_id.choices = [(0, _("Tout l'institut"))] + [
        (p.id, p.name) for p in Promotion.query.filter_by(is_active=True).order_by(Promotion.name)
    ]


@bp.route("/nouvelle", methods=["GET", "POST"], defaults={"news_id": None})
@bp.route("/<int:news_id>/modifier", methods=["GET", "POST"])
@admin_required
def edit(news_id):
    item = db.get_or_404(News, news_id) if news_id else None
    form = NewsForm(obj=item)
    _form_choices(form)
    if request.method == "GET" and item:
        form.category_id.data = item.category_id or 0
        form.promotion_id.data = item.promotion_id or 0
    if form.validate_on_submit():
        if item is None:
            item = News(author_id=current_user.id)
            db.session.add(item)
        was_published = item.is_published
        item.title = form.title.data
        item.body = form.body.data.strip()
        item.category_id = form.category_id.data or None
        item.promotion_id = form.promotion_id.data or None
        item.is_pinned = form.is_pinned.data
        item.is_published = form.is_published.data
        if item.is_published and not was_published:
            item.published_at = item.published_at or utcnow()
            db.session.flush()
            notify(
                recipients(item.promotion_id),
                kind="news",
                title=item.title,
                url=url_for("news.show", news_id=item.id),
                exclude=current_user.id,
            )
        db.session.commit()
        flash(_("Actualité enregistrée."), "success")
        return redirect(url_for("news.manage"))
    return render_template("news/edit.html", form=form, item=item)


@bp.route("/<int:news_id>/supprimer", methods=["POST"])
@admin_required
def delete(news_id):
    item = db.get_or_404(News, news_id)
    db.session.delete(item)
    db.session.commit()
    flash(_("Actualité supprimée."), "success")
    return redirect(url_for("news.manage"))
