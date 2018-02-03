from flask import Flask
from flask import send_from_directory
from flask import render_template
from flask_htmlmin import HTMLMIN

app = Flask(__name__)

app.config['MINIFY_PAGE'] = True

HTMLMIN(app)

@app.route('/')
def home():
	return render_template('index.html', title='Eculum | Find meaning in your social media audience') 

@app.route('/about')
def about():
	return render_template('about.html', title='About | Eculum')


@app.route('/terms')
def terms():
	return render_template('terms.html', title='Terms & Condition | Eculum')

@app.route('/privacy')
def privacy():
	return render_template('privacy.html', title='Privacy Policy | Eculum')

@app.route('/site-map')
def sitemap():
	return render_template('sitemap.xml')

if __name__ == '__main__':
	app.run(host='0.0.0.0')
