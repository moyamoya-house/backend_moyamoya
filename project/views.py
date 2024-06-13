from flask import request, jsonify, Blueprint
from project.models import User, Moyamoya, Chats, Follow, Pots
from project import db, create_app
from datetime import datetime

bp = Blueprint('main',__name__)

# user 全体取得
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

# user createメソッド
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

# user単体取得
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

# user 更新処理
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

# user 削除メソッド
@bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'user deleted successfully'}), 200
    else:
        return jsonify({'error': 'user not found'}), 404


# MoyamoyaテーブルcrudAPI作成

# moyamoya 全件取得
@bp.route('/moyamoya',methods=['GET'])
def get_moyamoya_all():
    moyamoya_all = Moyamoya.query.all()
    moyamoyas_data = []
    
    for moyamoya in moyamoya_all:
        moyamoya_data = {
            'id': moyamoya.moyamoya_id,
            'post': moyamoya.moyamoya_post,
            'user': moyamoya.post_user_id,
            'created_at': moyamoya.created_at.strftime("%Y-%m-%d %H:%M:%S") if moyamoya.created_at else None
        }
        moyamoyas_data.append(moyamoya_data)
    return jsonify(moyamoyas_data), 200


# moyamoya create
@bp.route('/moyamoya',methods=['POST'])
def create_moyamoya():
    data = request.get_json()
    moyamoya_post = data.get('post')
    moyamoya_user = data.get('user_id')
    
    if moyamoya_post and moyamoya_user:
        moyamoya = Moyamoya(
            moyamoya_post = moyamoya_post,
            post_user_id = moyamoya_user,
            created_at = datetime.utcnow()
        )
        db.session.add(moyamoya)
        db.session.commit()
        return jsonify({
            'id': moyamoya.moyamoya_id,
            'post': moyamoya.moyamoya_post,
            'user_id': moyamoya.post_user_id,
            'created_at': moyamoya.created_at
        }), 201
    else:
        return jsonify({'error': 'Missingrequired fields'}), 400

# moyamoya データ単体取得
@bp.route('/moyamoya/<int:id>',methods=['GET'])
def get_moyamoya(id):
    moyamoya = Moyamoya.query.get(id)
    if moyamoya:
        moyamoya_data = {
            'id': moyamoya.moyamoya_id,
            'post': moyamoya.moyamoya_post,
            'user_id': moyamoya.post_user_id,
            'created_at': moyamoya.created_at
        }
        return jsonify(moyamoya_data), 200
    else:
        return jsonify({'error': 'moyamoya not found'}), 404

# moyamoya 更新処理
@bp.route('/moyamoya/<int:id>',methods=['PUT'])
def update_moyamoya(id):
    moyamoya = Moyamoya.query.get(id)
    if moyamoya:
        data = request.get_json()
        post = data.get('post')
        if post:
            moyamoya.moyamoya_post = post
        db.session.commit()
        return jsonify({'message': 'moyamoya updated successfully'}), 200
    else:
        return jsonify({'error': 'moyamoya not found'})

# moyamoya 削除メソッド
@bp.route('/moyamoya/<int:id>',methods=['DELETE'])
def delete_moyamoya(id):
    moyamoya = Moyamoya.query.get(id)
    if moyamoya:
        db.session.delete(moyamoya)
        db.session.commit()
        return jsonify({'message': 'moyamoya deleted successfully'})
    else:
        return jsonify({'error': 'moyamoya not found'}), 404

