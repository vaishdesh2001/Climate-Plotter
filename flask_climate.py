from flask import Flask, render_template, flash
from forms import Get_Plot
import Climate_Runner_App

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/Get Plot", methods=['GET', 'POST'])
def get_plot():
    form = Get_Plot()
    if form.validate_on_submit():
        str_input = form.str_input.data
        plot_command = str_input
        city = Climate_Runner_App.main(str_input)
        if city is None:
            flash(f'"{form.str_input.data}" does not contain a city, or the city has a population lesser than 100k!',
                  'danger')
            return render_template('get_plot.html', title='Get Plot', form=form)
        flash(f'Plot created for "{form.str_input.data}" !', 'light')
        return render_template('output.html', command=plot_command, city=city)
    return render_template('get_plot.html', title='Get Plot', form=form)


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
