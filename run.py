'''
    imports the app variable from the Flask instance called stock_analysis_app from
    stock_analysis_app/__init__.py, and call app.run()
'''
from app_folder import app

if __name__ == '__main__':
    app.run()
