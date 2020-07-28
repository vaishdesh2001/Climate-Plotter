# Climate-Plotter

Climate Plotter is a unique python-driven search engine solely focused on pulling and plotting climate data.
https://climate-plotter.herokuapp.com/

## Description

This app helps anyone interested in understanding climatic stats of a given city over the months in a year. This project also allows users to compare weather trends for two cities. It displays information through a plotted graph. With data for over 4000 cities, this tool covers an extensive database.

## Getting Started

This is a Flask application that runs on the Heroku platform.

- In the root directory, wsgi.py, runtime.txt, requirements.txt, nltk.txt, Procfile are all the files required for the deployment of this Flask app.
- Within the app directory, main.py is the Flask runner application
  - all the front-end files(HTML, CSS and JS files) accessed by main.py are stored within the folder named static. The main html files are stored under the templates directory.
  - all files generated during the course of execution of the program are stored in the career_files folder and the templates folder.
  - this flask app runs Climate_Runner_App.py that runs the main part of the program like collecting climate data and generating a climate plot for a city(or two cities)
- Climate_Runner_App.py  contains the main algorithm for plotting the climate data.

## Running the Code

To run this application from your local machine, navigate to the root directory and run this from the command line
```bash
python wsgi.py
```
Copy and paste the link displayed onto your browser.
The Climate-Plotter is up and running!

## Usage

Click 'Get a Climate Plot!' and enter a sentence containing a city(or two cities) and a climate statistic and hit enter!
