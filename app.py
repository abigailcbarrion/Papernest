from flask import Flask, url_for
from flask_wtf.csrf import CSRFProtect
from forms import LoginForm, RegistrationForm
from utilities.storage import get_featured_author
from utilities.cart import get_cart_count

from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.cart_routes import cart_bp
from routes.checkout_routes import checkout_bp
from routes.admin_routes import admin_bp
from routes.product_routes import product_bp
from routes.auth_routes import auth_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    app.config['SECRET_KEY'] = '631539ff18360356'
    
    # Keep CSRF enabled afor forms but exempt specific routes
    csrf = CSRFProtect(app)
    csrf.init_app(app)

    csrf.exempt(main_bp)    
    
    # Exempt the cart blueprint from CSRF
    csrf.exempt(cart_bp)

    csrf.exempt(admin_bp)
    
    # Also exempt the checkout blueprint from CSRF
    csrf.exempt(checkout_bp)
    
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(cart_bp, url_prefix='/')
    app.register_blueprint(checkout_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/')
    app.register_blueprint(product_bp, url_prefix='/')

    @app.context_processor
    def inject_cart_count():
        """Make cart count available in all templates"""
        try:
            count = get_cart_count()
            return {'cart_count': count}  # Return a dictionary, not just the count
        except Exception as e:
            print(f"Error getting cart count for context: {str(e)}")
            return {'cart_count': 0}  # Return dict with default value

    @app.context_processor
    def inject_common_variables():
        featured_author = get_featured_author()
        return {'featured_author': featured_author}

    @app.context_processor
    def inject_forms():
        login_form = LoginForm()
        registration_form = RegistrationForm()
        
        login_form.email.id = 'login_email'
        login_form.password.id = 'login_password'
        login_form.csrf_token.id = 'login_csrf_token'
        
        registration_form.username.id = 'register_username'
        registration_form.password.id = 'register_password'
        registration_form.csrf_token.id = 'register_csrf_token'
        
        return {
            'login_form': login_form,
            'registration_form': registration_form
        }
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)