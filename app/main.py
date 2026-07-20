from sanic import Sanic
from app.api.auth import login_bp
from app.api.payments import payment_bp
from app.api.admin import admin_bp
from app.api.profile import profile_bp
from middleware.middleware import inject_session, close_session

app = Sanic("dimatech_test")
app.config.load_environment_vars(prefix="SANIC_")

app.blueprint(login_bp)
app.blueprint(profile_bp)
app.blueprint(admin_bp)
app.blueprint(payment_bp)

app.middleware(inject_session, attach_to="request")
app.middleware(close_session, attach_to="response")

if __name__ == '__main__':
    app.run()
