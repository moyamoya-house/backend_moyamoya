from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_login import current_user, login_user , login_required
from project.models import User, Moyamoya, Chats, Follow, Pots, Nice
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from project import db, create_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

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
    name = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    prof_image = request.files['profimage']
    
    prof_image_filename = secure_filename(prof_image.filename)
    prof_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'],prof_image_filename))
    
    if password:
        hash_password = generate_password_hash(password, method='sha256')
    
    if name and password and email:
        user = User(
            user_name = name,
            password = hash_password,
            e_mail = email,
            prof_image = prof_image_filename,
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
            'second_image': user.second_image,
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
            'second_image': user.second_image,
            'comment': user.prof_comment,
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
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        comment = request.form.get('comment')
        prof_image = request.files['profimage']
        second_image = request.files['secondimage']
    
        if prof_image:
            prof_image_filename = secure_filename(prof_image.filename)
            prof_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], prof_image_filename))
            user.prof_image = prof_image_filename

        if second_image:
            second_image_filename = secure_filename(second_image.filename)
            second_image.save(os.path.join(current_app.config['UPLOAD_FOLDER_SECOND'], second_image_filename))
            user.second_image = second_image_filename
        if name :
            user.user_name = name
        if password:
            user.password = password
        if email:
            user.e_mail = email
        if comment:
            user.prof_comment = comment
        
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


# login処理
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(user_name=username).first()
    
    if user :
        if check_password_hash(user.password,password):
            login_user(user)
            access_token = create_access_token(identity=user.user_id)
            return jsonify({'token':access_token}), 200
        else:
            return jsonify({'error': 'login error'}), 400
        

# mypage
@bp.route('/mypage', methods=['GET'])
@jwt_required()
def mypage():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user:
        return jsonify({
            'id': user.user_id,
            'name': user.user_name,
            'password': user.password,
            'email': user.e_mail,
            'prof_image': user.prof_image,
            'second_image': user.second_image,
            'prof_comment': user.prof_comment,
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404

# prof_imageパス
@bp.route('/prof_image/<filename>', methods=['GET'])
def prof_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# second_imageパス
@bp.route('/second_image/<filename>', methods=['GET'])
def second_prof_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_SECOND'],filename)

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
            'user_id': moyamoya.post_user_id,
            'created_at': moyamoya.created_at.strftime("%Y-%m-%d %H:%M:%S") if moyamoya.created_at else None
        }
        moyamoyas_data.append(moyamoya_data)
    return jsonify(moyamoyas_data), 200


# moyamoya create
@bp.route('/moyamoya',methods=['POST'])
@jwt_required()
def create_moyamoya():
    data = request.get_json()
    moyamoya_post = data.get('post')
    moyamoya_user = get_jwt_identity()
    
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

# userごとの投稿
@bp.route('/moyamoya_user',methods=["GET"])
@jwt_required()
def moyamoya_user():
    moyamoya_user = get_jwt_identity()
    moyamoyas = Moyamoya.query.filter_by(post_user_id=moyamoya_user)
    moyamoya_all = []
    for moyamoyas in moyamoyas:
        moyamoya_data = {
            'id': moyamoyas.moyamoya_id,
            'post': moyamoyas.moyamoya_post,
            'user_id': moyamoyas.post_user_id,
            'created_at': moyamoyas.created_at
        }
        moyamoya_all.append(moyamoya_data)
    return jsonify(moyamoya_all), 200

# フォローユーザーの投稿
@bp.route('/moyamoya_follow', methods=['GET'])
@jwt_required()
def moyamoya_follow():
    current_user = get_jwt_identity()
    
    if current_user:
        following_users = Follow.query.filter_by(follower_user_id=current_user).all()
        following_user_ids = [follow.followed_user_id for follow in following_users]
        
        posts = Moyamoya.query.filter(Moyamoya.post_user_id.in_(following_user_ids)).all()
        
        result = []
        for post in posts:
            result.append({
                'id': post.moyamoya_id,
                'post': post.moyamoya_post,
                'user_id': post.post_user_id,
                'created_at': post.created_at
            })
        
        return jsonify(result), 200
    
    return jsonify({"msg": "User not found"}), 404


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

# potsテーブル crudAPI

# pots 全件取得
@bp.route('/pots',methods=['GET'])
def get_pots_all():
    pots = Pots.query.all()
    pots_data = []
    
    for pot in pots:
        pot_data = {
            "id": pot.pots_id,
            "audio": pot.audio_file,
            "stress_level": pot.stress_level,
            "emotion_score": pot.emotion_score,
            "user_id": pot.pots_user_id,
            "created_at": pot.created_at
        }
        pots_data.append(pot_data)
    return jsonify(pots_data), 200

# pots create
@bp.route('/pots',methods=['POST'])
def create_pots():
    data = request.get_json()
    audio = data.get('audio')
    emotion = data.get('emotion')
    stress = data.get('stress')
    user_id = data.get('user_id')
    
    if audio and emotion and stress and user_id:
        pots = Pots(
            audio_file = audio,
            emotion_score = emotion,
            stress_level = stress,
            pots_user_id = user_id
        )
        db.session.add(pots)
        db.session.commit()
        return jsonify({
            'id': pots.pots_id,
            'audio_file': pots.audio_file,
            "emotion_score": pots.emotion_score,
            'stress': pots.stress_level,
            'user_id': pots.pots_user_id,
            'created_at': pots.created_at
        }), 201
    else:
        return jsonify({'error': 'Missingrequired fields'}), 400

# pots データ単体取得
@bp.route('/pots/<int:id>',methods=['GET'])
def get_pots(id):
    pots = Pots.query.get(id)
    if pots:
        pots_data = {
            'id': pots.pots_id,
            'audio': pots.audio_file,
            'emotion_score': pots.emotion_score,
            'stress_level': pots.stress_level,
            'pots_user_id': pots.pots_user_id,
            'created_at': pots.created_at
        }
        return jsonify(pots_data), 200
    else:
        return jsonify({'error': 'pots not found'}), 404

# pots updateメソッド
@bp.route('/pots/<int:id>', methods=['PUT'])
def update_pots(id):
    pots = Pots.query.get(id)
    if pots:
        data = request.get_json()
        emotion = data.get('emotion')
        stress = data.get('stress')
        if emotion:
            pots.emotion_score = emotion
        if stress:
            pots.stress_level = stress
        db.session.commit()
        return jsonify({'message': 'pots updated successfully'}), 200
    else:
        return jsonify({'error': 'pots not found'}), 404

# pots deleteメソッド
@bp.route('/pots/<int:id>', methods=['DELETE'])
def delete_pots(id):
    pots = Pots.query.get(id)
    if pots:
        db.session.delete(pots)
        db.session.commit()
        return jsonify({'message': 'pots deleted successfully'}), 200
    else:
        return jsonify({'error': 'pots not found'}), 404


# follow crudAPI

# follow 全件取得
@bp.route('/follows', methods=['GET'])
def get_follows_all():
    follow = Follow.query.all()
    follow_data = []
    
    for follows in follow:
        follows_data = {
            'id': follows.follow_id,
            'follower': follows.follower_user_id,
            'followed': follows.followed_user_id
        }
        follow_data.append(follows_data)
    return jsonify(follow_data)

# createAPI
@bp.route('/follow/<int:user_id>', methods=['POST'])
@jwt_required()
def create_follow(user_id):
    current_user_id = get_jwt_identity()
    # ユーザーをフォローしているか
    user_friendship = Follow.query.filter_by(follower_user_id=current_user_id,followed_user_id=user_id).first()
    if user_friendship:
        return jsonify({'error': 'Followed User'}),500
    
    friendship = Follow(
        follower_user_id = current_user_id,
        followed_user_id = user_id,
    )
    
    db.session.add(friendship)
    db.session.commit()
    return jsonify({
        'id': friendship.follow_id,
        'follower_user_id': friendship.follower_user_id,
        'followed_user_id': friendship.followed_user_id
    }),200


# 自分のフォロワー
@bp.route('/follower',methods=['GET'])
@jwt_required()
def get_follower():
    user = get_jwt_identity()
    
    if user:
        # フォロワーユーザーを取得
        followers_count = Follow.query.filter_by(followed_user_id=user).count()
        # フォロー中のユーザーをカウント
        following_count = Follow.query.filter_by(follower_user_id=user).count()
    
    return jsonify({
        'follower':followers_count,
        'following': following_count,
    }),200

# 他者のフォロー
@bp.route('/user_followers/<int:user_id>',methods=['GET'])
def user_follower(user_id):
    # フォローしているユーザーを取得
    followers_count = Follow.query.filter_by(followed_user_id=user_id).count()
    # フォロー中のユーザーをカウント
    following_count = Follow.query.filter_by(follower_user_id=user_id).count()
    
    return jsonify({
        'follower':followers_count,
        'following': following_count,
    }),200

# chats crudAPI

# chats 全件取得
@bp.route('/chats',methods=['GET'])
def get_chat_all():
    chat = Chats.query.all()
    chats_data = []
    
    for chats in chat:
        chat_data = {
            'id': chats.chat_id,
            'message': chats.message,
            'send_user_id': chats.send_user_id,
            'receiver_user_id': chats.receiver_user_id,
            'created_at': chats.created_at
        }
        chats_data.append(chat_data)
    return jsonify(chats_data)



# Nice crudAPI

# Nice 全件取得
@bp.route('/nice_all',methods=['GET'])
def nice_all():
    nice = Nice.query.all()
    
    nices_data = []
    
    for nices in nice:
        nice_data = {
            'id': nices.nice_id,
            'post_id': nices.post_id,
            'user_id': nices.user_id
        }
        nices_data.append(nice_data)
    return jsonify(nices_data),200

# Nice create
@bp.route('/nice/<int:post_id>',methods=['POST'])
@jwt_required()
def nice(post_id):
    current_user = get_jwt_identity()
    nice = Nice.query.filter_by(post_id=post_id, user_id=current_user).first()
    
    # すでにいいねしている場合
    if nice:
        db.session.delete(nice)
        liked= False
    else:
        # いいねしていない場合
        new_nice = Nice(post_id=post_id,user_id=current_user)
        db.session.add(new_nice)
        liked=True
    db.session.commit()
    
    return jsonify({"liked": liked}),200
