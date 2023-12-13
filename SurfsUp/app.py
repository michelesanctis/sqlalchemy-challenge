# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask (__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")

def home():
    """List of available api routes:"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    """Return a list of all Precipitation Data"""
    # Query precipitation
    last_year_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-23").\
        filter(Measurement.date <= "2017-08-23").all()

    # Convert the list to a dictionary for JSON response
    last_year_dic = [{"date": date, "Precipitation": prcp} for date, prcp in last_year_data]

    # Close session
    session.close()

    #Return JSON
    return jsonify(last_year_dic)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""

    # Query stations
    all_stations = session.query(Station.station).all()

    # Convert list of tuples into normal list
    station_dic = list(np.ravel(all_stations))

    # Close session
    session.close()

    #Return JSON
    return jsonify(station_dic)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return dates and temperature observations of the most-active station for the previous year of data."""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Using the most active station id
    # Query the last 12 months of temperature observation data for USC00519281 station
    last12monthsT = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >="2016-08-23").\
        filter(Measurement.date <="2017-08-23").all()

    #Convert the list of tobs to a dictionary for JSON response
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in last12monthsT]
    
    # Close session
    session.close()
    
    #Return JSON
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    start = request.args.get('start', '2016-08-23')

    # Query DB filtering start date
    all_tobs= session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()

    #Create a dictionary to store the data
    start_tobs_list = []
    for min, avg, max in all_tobs:
        start_tobs_dic = {
        "TMIN": min,
        "TAVG": avg,
        "TMAX": max
        }
        start_tobs_list.append(start_tobs_dic)

    # Close session
    session.close()    
    
    return jsonify(start_tobs_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    start = request.args.get('start', '2016-08-23')
    end = request.args.get('end', '2017-08-23')

    # Query DB filtering start date
    startendtobs= session.query(func.min(Measurement.tobs), 
                                func.avg(Measurement.tobs), 
                                func.max(Measurement.tobs)).\
                                filter(Measurement.date >= start).\
                                filter(Measurement.date <= end).all()
    
    #Create a dictionary to store the data
    start_end_list = []
    for min, avg, max in startendtobs:
        start_end_dic = {
        "TMIN": min,
        "TAVG": avg,
        "TMAX": max
        }
        start_end_list.append(start_end_dic)

    # Close session
    session.close()

    return jsonify(start_end_list)

if __name__ == "__main__":
    app.run(debug=True)
