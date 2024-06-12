from flask import request, jsonify, Blueprint
from project.models import User
from project import db, create_app
from datetime import datetime

bp = Blueprint('main',__name__)

@bp.route('/users',methods=['GET'])
def get_users():
    users = User.query.all()
    user_data = []
    for user in users:
        users_data = {
        'id': user.user_id,
        'user_name': user.user_name,
        'password': user.password,
        'email': user.e_mail,
        'prof_image': user.prof_image,
        'created_at': user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
        }
        user_data.append(users_data)
    return jsonify(user_data), 200

@bp.route('/users',methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    email = data.get('email')
    prof_image = data.get('prof_image')
    
    if name and password and email:
        user = User(
            user_name = name,
            password = password,
            e_mail = email,
            prof_image = prof_image,
            created_at = datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'id': user.user_id,
            'name': user.user_name,
            'password': user.password,
            'email': user.e_mail,
            'prof_image': user.prof_image,
            'created_at': user.created_at
        }), 201
    else:
        return jsonify({'error': 'Missing required fields'}), 400


@bp.route('/users/<int:id>',methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        user_data = {
            'id': user.user_id,
            'name': user.user_name,
            'password': user.password,
            'email': user.e_mail,
            'prof_image': user.prof_image,
            'created_at': user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None
        }
        return jsonify(user_data), 200
    else:
        return jsonify({'error': 'user not found'}), 404


@bp.route('/users/<int:id>',methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if user:
        data = request.get_json()
        name = data.get('name')
        password = data.get('password')
        email = data.get('email')
        prof_image = data.get('profimage')
        if name :
            user.user_name = name
        if password:
            user.password = password
        if email:
            user.e_mail = email
        if prof_image:
            user.prof_image = prof_image
        
        db.session.commit()
        return jsonify({'message': 'user updated successfully'}), 200
    else:
        return jsonify({'error': 'user not found'}), 404


@bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'user deleted successfully'}), 200
    else:
        return jsonify({'error': 'user not found'}), 404