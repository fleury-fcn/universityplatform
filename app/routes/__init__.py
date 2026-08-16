
from .main import mainbp
from .auth import authbp
from .principale import principalebp
from .syllabus import syllabusbp
from .registration import registrationbp
from .courses import coursesbp
from .clubs import clubsbp
from .profile import profilebp
from .addsyllabus import addsyllabusbp
from .books import books_bp
from .tuyaux import tuyauxbp
from .admin import adminbp
from .messagerie import messagerie_bp
from .maintenance import maintenancebp
from .actualites import actualites_bp
from .enseignants import enseignants_bp
from .academique import academique_bp
from .dashboard import dashboard_bp


all_blueprints = [
    mainbp,
    authbp,
    principalebp,
    syllabusbp,
    registrationbp,
    coursesbp,
    clubsbp,
    profilebp,
    addsyllabusbp,
    books_bp,
    tuyauxbp,
    adminbp,
    messagerie_bp,
    maintenancebp,
    actualites_bp,
    enseignants_bp,
    academique_bp,
    dashboard_bp
]