# Import the dependencies.
from flask import Flask, jsonify, g
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
import numpy as np

#################################################
# Database Setup
#################################################

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
print('Keys: '
)
print(Base.classes.keys())

# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)
# session = Session()
# This prevents concurrent thread issue
Session = sessionmaker(bind=engine)

#################################################
# Flask Setup
#################################################

# app = Flask(__name__)
app = Flask("climate-starter")

@app.before_request
def before_request():
    g.session = Session()

@app.teardown_request
def teardown_request(exception):
    session = g.get('session')
    if session is not None:
        session.close()

#################################################
# Flask Routes
#################################################

@app.route('/')
def index():
    return """
    Routes:<br/>
        <a href="/api/v1.0/measurements">/api/v1.0/measurements</a><br/>
        <a href="/api/v1.0/measurements/{id}">/api/v1.0/measurements/{id}</a><br/>
        <a href="/api/v1.0/stations">/api/v1.0/stations</a><br/>
        <a href="/api/v1.0/stations/{id}">/api/v1.0/stations/{id}</a><br/>
    """

@app.route("/api/v1.0/measurements")
def measurements():
    session = g.session  # Get the session from g object
    # Query all measurements
    results = session.query(Measurement).all()

    # Convert the results to dictionaries
    all_measurements = []
    for result in results:
        measurement_dict = {column.name: getattr(result, column.name) for column in result.__table__.columns}
        all_measurements.append(measurement_dict)

    return jsonify(all_measurements)


@app.route("/api/v1.0/measurements/<int:id>")
def measurement(id):
    session = g.session  # Get the session from g object
    # Query the measurement by id
    result = session.query(Measurement).get(id)

    # Convert the result into a dictionary
    measurement = {c.name: getattr(result, c.name) for c in Measurement.__table__.columns}

    return jsonify(measurement)


@app.route("/api/v1.0/stations")
def stations():
    session = g.session  # Get the session from g object
    # Query all stations
    results = session.query(Station).all()

    # Convert list of tuples into normal list
    all_stations = []
    for result in results:
        station_dict = {column.name: getattr(result, column.name) for column in result.__table__.columns}
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/stations/<int:id>")
def station(id):
    session = g.session  # Get the session from g object
    # Query the station by id
    result = session.query(Station).get(id)

    # Convert the result into a dictionary
    station = {c.name: getattr(result, c.name) for c in Station.__table__.columns}

    return jsonify(station)

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = g.session  # Get the session from g object
    # Query for the last 12 months of precipitation data
    results = (session.query(Measurement.date, Measurement.prcp)
                      .filter(Measurement.date >= '2017-08-23')  # replace with the date one year before your most recent data
                      .all())

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/tobs")
def tobs():
    session = g.session  # Get the session from g object
    # Query for the last year of temperature data for the most active station
    most_active_station = 'USC00519281'  # replace with your most active station
    results = (session.query(Measurement.date, Measurement.tobs)
                      .filter(Measurement.station == most_active_station)
                      .filter(Measurement.date >= '2017-08-23')  # replace with the date one year before your most recent data
                      .all())

    # Convert the query results to a dictionary
    temp_data = {date: temp for date, temp in results}
    
    return jsonify(temp_data)


@app.route("/api/v1.0/<start>")
def start(start):
    session = g.session  # Get the session from g object
    # Query minimum, average and maximum temperatures for all dates greater than or equal to the start date
    results = (session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
                      .filter(Measurement.date >= start).all())

    # Convert the query results to a list
    temps = list(np.ravel(results))

    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = g.session  # Get the session from g object
    # Query minimum, average and maximum temperatures for dates between the start and end date inclusive
    results = (session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
                      .filter(Measurement.date >= start)
                      .filter(Measurement.date <= end).all())

    # Convert the query results to a list
    temps = list(np.ravel(results))

    return jsonify(temps)



if __name__ == "__main__":
    app.run(port=7000, debug=True)
    # app.run(debug=True)
