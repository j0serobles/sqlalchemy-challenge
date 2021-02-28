"""
Routes
/
Home page.
List all routes that are available.



/api/v1.0/precipitation
Convert the query results to a dictionary using date as the key and prcp as the value.
Return the JSON representation of your dictionary.


/api/v1.0/stations
Return a JSON list of stations from the dataset.


/api/v1.0/tobs
Query the dates and temperature observations of the most active station for the last year of data.
Return a JSON list of temperature observations (TOBS) for the previous year.



/api/v1.0/<start> and /api/v1.0/<start>/<end>
Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.



Hints
You will need to join the station and measurement tables for some of the queries.
Use Flask jsonify to convert your API data into a valid JSON response object.
"""
import sys
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station     = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-mm-dd and /api/v1.0/YYYY-mm-dd/YYYY-mm-dd"
    )


@app.route("/api/v1.0/names")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(Passenger.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of date,precipitation value pairs """
    # Query all records
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    all_records = []
    for date, prcp, in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_records.append(prcp_dict)

    return jsonify(all_records)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of date,precipitation value pairs """
    # Query all records
    results = session.query(Station.station).all()

    session.close()
    all_records = list(np.ravel(results))
    
    
    return jsonify(all_records)

@app.route("/api/v1.0/topbs")
def topbs():
    
    session = Session(engine)
    max_date = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0], '%Y-%m-%d')
    min_date = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0], '%Y-%m-%d') - dt.timedelta(days=366)
    
    sel = [Measurement.station, func.count(Measurement.station)]
    top_station = session.query(*sel)\
    .group_by(Measurement.station)\
    .order_by(desc(func.count(Measurement.station))).first()
    top_station_id = top_station[0]
    
    sel = [Measurement.date, Measurement.tobs]
    results = session.query(*sel)\
    .filter(Measurement.station == top_station_id)\
    .filter(Measurement.date.between(min_date, max_date)).all()
    session.close()
    
    all_records = []
    for date, tobs in results:
        temp_dict         = {}
        temp_dict["date"] = date,
        temp_dict["tobs"] = tobs

        all_records.append(temp_dict)
        
    return jsonify(all_records)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end=""):
    print("Start: " + start +  ", End: " + end, file= sys.stderr)
    
    if start == end:
         print('Start and End dates are equal!', file=sys.stderr)
         return('Start and End dates are equal - Please specify end date later than start date')

    min_date = dt.datetime.strptime(start, '%Y-%m-%d')
       
    session  = Session(engine);
    
    # If end date is null, set it to the latest date in Measurement
    if not end:
        max_date = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0], '%Y-%m-%d')
    else:
        max_date = dt.datetime.strptime(end, '%Y-%m-%d')
            
        
    print(dt.datetime.strftime(min_date, '%Y-%m-%d'), file=sys.stderr)
    print(dt.datetime.strftime(max_date, '%Y-%m-%d'), file=sys.stderr)

            
    sel = [ Station.station,
            Station.name,
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)]
      
    temp_averages = session.query(*sel)\
        .filter(Measurement.station == Station.station)\
        .filter(Measurement.date.between(min_date, max_date))\
        .filter(Measurement.tobs != None)\
        .group_by(Station.station,Station.name)\
        .order_by(Measurement.date).all()
    
    session.close()
    
    #print(temp_averages[0], file=sys.stderr)
                                               
    all_records = []
    for station, name, min_temp, avg_temp, max_temp in temp_averages:
        temp_dict         = {}
        temp_dict["station"] = station,
        temp_dict["name"] = name
        temp_dict["min"]  = min_temp
        temp_dict["avg"]  = avg_temp
        temp_dict["max"]  = max_temp
        all_records.append(temp_dict)
        
    return jsonify(all_records)

   
                                               
if __name__ == '__main__':
    app.run(debug=True)
