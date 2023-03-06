# Deficiencies
from dateutil.relativedelta import relativedelta
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base

# Create engine and connect to the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create app instance
app = Flask(__name__)

# Define routes


@app.route("/")
def home():
    return (
        f"Welcome to Hawaii Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date <br/>"
        f"/api/v1.0/start_date/end_date"
    )

# Define the precipitation route to return precipitation data for the last 12 months


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session link to the database
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    query_date = last_date - dt.timedelta(days=365)

    # Query for the date and precipitation for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= query_date).all()
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_data = {}
    for date, prcp in results:
        precipitation_data[date] = prcp

    return jsonify(precipitation_data)

# Return a JSON list of stations from the dataset


@app.route("/api/v1.0/stations")
def stations():
    # Create session link to the database
    session = Session(engine)

    # Query for the stations in the dataset
    results = session.query(Station.station).all()
    session.close()

    # Convert the query results to a list
    station_list = list(np.ravel(results))

    return jsonify(station_list)

# Query the dates and temperature observations of the most-active station for the previous year of data


@app.route("/api/v1.0/tobs")
def tobs():
    # Create session link to the database
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    query_date = last_date - dt.timedelta(days=365)

    # Query for the most active station
    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by((Measurement.station).order_by(func.count))

 # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

# Define the Start and End route


@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = start_date + relativedelta(years=1)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()
    temperatures = []
    for min_temp, avg_temp, max_temp in results:
        temperature_dict = {}
        temperature_dict["Minimum Temperature"] = min_temp
        temperature_dict["Average Temperature"] = avg_temp
        temperature_dict["Maximum Temperature"] = max_temp
        temperatures.append(temperature_dict)
    return jsonify(temperatures)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    session.close()
    temperatures = []
    for min_temp, avg_temp, max_temp in results:
        temperature_dict = {}
        temperature_dict["Minimum Temperature"] = min_temp
        temperature_dict["Average Temperature"] = avg_temp
        temperature_dict["Maximum Temperature"] = max_temp
        temperatures.append(temperature_dict)
    return jsonify(temperatures)


if __name__ == '__main__':
    app.run(debug=True)
