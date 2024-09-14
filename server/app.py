#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api=Api(app)

class HeroesResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([{
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name
        } for hero in heroes])

class SingleHeroResource(Resource):
    def get(self, id):
        hero = db.session.get(Hero, id)
        if hero:
            return hero.to_dict(), 200  # Use the to_dict method to serialize
        return {'error': 'Hero not found'}, 404

class PowersResource(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([{
            'id': power.id,
            'name': power.name,
            'description': power.description
        } for power in powers])

class SinglePowerResource(Resource):
    def get(self, id):
        power = db.session.get(Power, id)
        if power:
            return {
                'id': power.id,
                'name': power.name,
                'description': power.description
            }, 200
        return {'error': 'Power not found'}, 404

    def patch(self, id):
        power = db.session.get(Power, id)
        if not power:
            return {'error': 'Power not found'}, 404

        data = request.get_json()
        try:
            if 'description' in data:
                power.description = data['description']
            db.session.commit()
            return power.to_dict(), 200
        except ValueError as e:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400

class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_hero_power = HeroPower(
                strength=data['strength'],
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            db.session.add(new_hero_power)
            db.session.commit()

            return new_hero_power.to_dict(), 200
        except ValueError as e:
            return {'errors': ['validation errors']}, 400

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

api.add_resource(HeroesResource, '/heroes')
api.add_resource(SingleHeroResource, '/heroes/<int:id>')
api.add_resource(PowersResource, '/powers')
api.add_resource(SinglePowerResource, '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
