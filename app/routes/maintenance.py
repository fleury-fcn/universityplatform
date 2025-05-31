from flask import Blueprint, render_template
from flask_login import current_user
import os

maintenancebp = Blueprint('maintenance', __name__)

MAINTENANCE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'maintenance.flag')

def is_maintenance_mode():
    return os.path.exists(MAINTENANCE_FILE)

@maintenancebp.before_app_request
def check_maintenance():
    # Autorise les admins à accéder au site même en maintenance
    if is_maintenance_mode() and not (current_user.is_authenticated and getattr(current_user, 'role', None) == 'administrateur'):
        return render_template('maintenance.html'), 503