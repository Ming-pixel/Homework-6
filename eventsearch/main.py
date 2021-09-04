import json

import requests
import os
from flask import Flask, render_template, request, jsonify

template_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(template_dir, 'static')
print(template_dir)
app = Flask(__name__, template_folder=template_dir)


@app.route('/')
def index():
    return render_template('event.html')


@app.route('/event', methods=['GET'])
def event_search():
    from geolib import geohash
    API_KEY = 'API_KEY'
    keyword = request.args['keyword']
    print('keyword: ' + keyword)
    keyword.replace(' ', '+')
    category = request.args['category']
    segmentID = get_segmentID(category)
    distance = request.args['distance']
    here = request.args['here']
    if here.lower() == 'true':
        print('here radio selected')
        loc = request.args['loc']
        print('loc: ' + loc)
        loc_result = [x.strip() for x in loc.split(',')]
        print(loc_result)
        lat = loc_result[0]
        lng = loc_result[1]
    else:
        print('location radio selected')
        address = request.args['address']
        params = {
            'key': API_KEY,
            'address': address
        }
        baseurl = 'https://maps.googleapis.com/maps/api/geocode/json?'
        google_response = requests.get(baseurl, params=params).json()

        if google_response['status'] == 'OK':
            geometry = google_response['results'][0]['geometry']
            lat = geometry['location']['lat']
            lng = geometry['location']['lng']
        else:
            return 'Error occurs when get google geometry location', 500
    geohash = geohash.encode(lat, lng, 7)
    ticket_params = {
        'apikey': 'apikey',
        'keyword': keyword,
        'radius': distance,
        'unit': 'miles',
        'geoPoint': geohash
    }
    if segmentID != 'default' and segmentID != 'not support':
        ticket_params['segmentId'] = segmentID
    ticket_url = 'https://app.ticketmaster.com/discovery/v2/events.json?'
    ticket_response = requests.get(ticket_url, params=ticket_params).json()
    print(ticket_response)
    return jsonify(ticket_response)


@app.route('/eventdetails', methods=['GET'])
def event_details():
    id = request.args['id']
    detail_params = {
        'apikey': 'apikey'
    }
    detail_url = 'https://app.ticketmaster.com/discovery/v2/events/'
    detail_url = detail_url + id + '?'
    detail_response = requests.get(detail_url, params=detail_params).json()
    print(detail_response)
    return jsonify(detail_response)


def get_segmentID(category):
    if category.lower() == 'default':
        return 'default'
    elif category.lower() == 'music':
        return 'KZFzniwnSyZfZ7v7nJ'
    elif category.lower() == 'sports':
        return 'KZFzniwnSyZfZ7v7nE'
    elif category.lower() == 'artstheatre'.lower():
        return 'KZFzniwnSyZfZ7v7na'
    elif category.lower() == 'film':
        return 'KZFzniwnSyZfZ7v7nn'
    elif category.lower() == 'miscellaneous':
        return 'KZFzniwnSyZfZ7v7n1'
    else:
        return 'not support'


if __name__ == "__main__":
    app.run(debug=True)
