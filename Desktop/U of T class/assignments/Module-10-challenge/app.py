# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def homepage():
    return (
        f"This is climate App Homepage<br/>Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2015-08-23/2017-08-23"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Starting from the most recent data point in the database.
    most_recent_date = session.query(measurement.date).order_by(
        measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    most_recent_date = most_recent_date[0]
    year_ago = dt.date.fromisoformat(
        most_recent_date) - relativedelta(months=12)

    # Perform a query to retrieve the data and precipitation scores
    data = session.query(measurement.date, measurement.prcp).filter(
        measurement.date >= year_ago).all()

    # Create a dictionary from data
    result_dict = dict(data)
    session.close()
    return jsonify(result_dict)


@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(station.station, station.name).all()

    # Create a dictionary from data
    result_dict = dict(station_list)
    session.close()
    return jsonify(result_dict)


@app.route("/api/v1.0/tobs")
def tobs():
    most_active = session.query(measurement.date, measurement.tobs).filter(
        measurement.station == 'USC00519281').filter(measurement.date >= '2016-08-23').all()

    # Create a dictionary from data
    result_dict = dict(most_active)
    session.close()
    return jsonify(result_dict)


# Creating a function that query based on dynamic date
def specified_date(start, end=None):
    if end:
        result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(
            measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    else:
        result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(
            measurement.tobs)).filter(measurement.date >= start).all()
    return result


@app.route("/api/v1.0/<start>")
def start(start):

  # Query using start date
    result_dict = specified_date(start)
    session.close()

    tobs_list = []

    # create a list from the result_dict and append it to tobs_list
    for min, avg, max in result_dict:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

  # Query using start and end date
    result_dict = specified_date(start, end)
    session.close()

    tobs_list = []

    # create a list from the result_dict and append it to tobs_list
    for min, avg, max in result_dict:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


if __name__ == '__main__':
    app.run(debug=True)
