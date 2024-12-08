from functools import wraps
from flask import request, jsonify, Blueprint, current_app, send_from_directory
from flask_login import current_user, login_user , login_required
from project.models import User, Moyamoya, Chats, Follow, Pots, Nice, Bookmark, Notification, GroupChat, GroupMember, HashTag, MoyamoyaHashtag
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token, decode_token, verify_jwt_in_request
from project import db, create_app,socket
from flask_socketio import emit, disconnect
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re
from project.notification import create_notifition
from project.emotion import analyze_sentiment
from project.audio_text import transcribe_audio
from project.hashtag import get_trending_hashtags
from pydub import AudioSegment
from project.openai import generate_stress_relief_suggestion

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
@bp.route('/users', methods=['POST'])
def create_user():
    name = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    prof_image = request.files.get('profimage')
    
    # 画像がアップロードされていない場合のデフォルト設定
    if prof_image:
        prof_image_filename = secure_filename(prof_image.filename)
        prof_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], prof_image_filename))
    else:
        prof_image_filename = None  # 画像がない場合はNoneを設定
    
    if password:
        hash_password = generate_password_hash(password, method='sha256')
    
    if name and password and email:
        user = User(
            user_name=name,
            password=hash_password,
            e_mail=email,
            prof_image=prof_image_filename,  # prof_image_filename がNoneでもOK
            created_at=datetime.utcnow()
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

# user更新処理
@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if user:
        try:
            name = request.form.get('name')
            password = request.form.get('password')
            email = request.form.get('email')
            comment = request.form.get('comment')
            prof_image = request.files.get('profimage')
            second_image = request.files.get('secondimage')

            # 変更の有無を確認するために取得データをプリント
            print("Received Data - name:", name, "password:", password, "email:", email, "comment:", comment, "prof_image", prof_image, "second_image", second_image)

            if prof_image:
                prof_image_filename = secure_filename(prof_image.filename)
                prof_image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], prof_image_filename))
                user.prof_image = prof_image_filename

            if second_image:
                second_image_filename = secure_filename(second_image.filename)
                second_image.save(os.path.join(current_app.config['UPLOAD_FOLDER_SECOND'], second_image_filename))
                user.second_image = second_image_filename

            if name:
                user.user_name = name
            if password:
                # 暗号化して保存する場合は以下の行をコメントアウトし、代わりに暗号化のコードを追加
                user.password = password
            if email:
                user.e_mail = email
            if comment:
                user.prof_comment = comment
            
            db.session.commit()
            return jsonify({'message': 'user updated successfully'}), 200
        
        except Exception as e:
            db.session.rollback()  # エラーがあった場合にロールバック
            print("Error updating user:", e)
            return jsonify({'error': 'Failed to update user'}), 500
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
        


# password reset
@bp.route('/password_reset', methods=['PUT'])
def password_reset():
    data = request.get_json()
    username = data.get('user_name')
    password = data.get('password')
    password_confilm = data.get('password_confilm')
    
    user = User.query.filter_by(user_name = username).first()
    
    if user and password==password_confilm:
        hash_password = generate_password_hash(password,method='sha256')
        user.password = hash_password
        db.session.commit()
        return jsonify({
            'name': user.user_name,
            'password': user.password
            }),200

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

# moyamoya全件取得
@bp.route('/moyamoya', methods=['GET'])
def get_moyamoya_all():
    moyamoya_all = Moyamoya.query.all()
    moyamoyas_data = []

    for moyamoya in moyamoya_all:
        nice_count = Nice.query.filter_by(post_id=moyamoya.moyamoya_id).count()
        
        # Moyamoya に関連付けられたハッシュタグを取得
        hashtags = [
            hashtag.tag_name
            for hashtag in HashTag.query.join(MoyamoyaHashtag).filter(MoyamoyaHashtag.moyamoya_id == moyamoya.moyamoya_id).all()
        ]
        
        moyamoya_data = {
            'id': moyamoya.moyamoya_id,
            'post': moyamoya.moyamoya_post,
            'user_id': moyamoya.post_user_id,
            'tags': hashtags,  # ハッシュタグをリストで返す
            'created_at': moyamoya.created_at.strftime("%Y-%m-%d %H:%M:%S") if moyamoya.created_at else None,
            'count': nice_count,
        }
        moyamoyas_data.append(moyamoya_data)
    
    return jsonify(moyamoyas_data), 200

# moyamoya create
@bp.route('/moyamoya', methods=['POST'])
@jwt_required()
def create_moyamoya():
    data = request.get_json()
    moyamoya_post = data.get('post')
    moyamoya_user = get_jwt_identity()

    if moyamoya_post and moyamoya_user:
        # 新しいMoyamoyaエントリを作成
        moyamoya = Moyamoya(
            moyamoya_post=moyamoya_post,
            post_user_id=moyamoya_user,
            created_at=datetime.utcnow()
        )
        db.session.add(moyamoya)
        db.session.flush()  # `moyamoya_id`を取得するために一時保存

        # ハッシュタグの抽出
        hashtags = re.findall(r'#\w+', moyamoya_post)

        for tag in hashtags:
            # ハッシュタグ名を正規化（例: 前後のスペース除去）
            tag_name = tag.strip().lower()

            # 既存のタグを検索
            existing_tag = HashTag.query.filter_by(tag_name=tag_name).first()

            if not existing_tag:
                # 新しいタグを作成
                new_tag = HashTag(tag_name=tag_name)
                db.session.add(new_tag)
                db.session.flush()  # `id`を取得するために一時保存
                tag_id = new_tag.tag_id
            else:
                tag_id = existing_tag.tag_id

            # MoyamoyaHashTagエントリを作成
            moyamoya_hashtag = MoyamoyaHashtag(
                moyamoya_id=moyamoya.moyamoya_id,
                tag_id=tag_id
            )
            db.session.add(moyamoya_hashtag)

        # 最終的なコミット
        db.session.commit()

        return jsonify({
            'id': moyamoya.moyamoya_id,
            'post': moyamoya.moyamoya_post,
            'user_id': moyamoya.post_user_id,
            'hashtags': hashtags,
            'created_at': moyamoya.created_at
        }), 201
    else:
        return jsonify({'error': 'Missing required fields'}), 400

# moyamoya データ単体取得
@bp.route('/moyamoya/<int:id>',methods=['GET'])
def get_moyamoya(id):
    moyamoya = Moyamoya.query.get(id)
    if moyamoya:
        moyamoya_data = {
            'id': moyamoya.moyamoya_id,
            'post': moyamoya.moyamoya_post,
            'user_id': moyamoya.post_user_id,
            'hash_tag': moyamoya.hash_tag,
            'created_at': moyamoya.created_at.strftime("%Y-%m-%d %H:%M:%S") if moyamoya.created_at else None,
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
    moyamoyas_data = []

    for moyamoya in moyamoyas:
        nice_count = Nice.query.filter_by(post_id=moyamoya.moyamoya_id).count()
        
        # Moyamoya に関連付けられたハッシュタグを取得
        hashtags = [
            hashtag.tag_name
            for hashtag in HashTag.query.join(MoyamoyaHashtag).filter(MoyamoyaHashtag.moyamoya_id == moyamoya.moyamoya_id).all()
        ]
        
        moyamoya_data = {
            'id': moyamoya.moyamoya_id,
            'post': moyamoya.moyamoya_post,
            'user_id': moyamoya.post_user_id,
            'tags': hashtags,  # ハッシュタグをリストで返す
            'created_at': moyamoya.created_at.strftime("%Y-%m-%d %H:%M:%S") if moyamoya.created_at else None,
            'count': nice_count,
        }
        moyamoyas_data.append(moyamoya_data)
    
    return jsonify(moyamoyas_data), 200

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
            nice_count = Nice.query.filter_by(post_id=post.moyamoya_id).count()
            
                    # Moyamoya に関連付けられたハッシュタグを取得
            hashtags = [
                hashtag.tag_name
                for hashtag in HashTag.query.join(MoyamoyaHashtag).filter(MoyamoyaHashtag.moyamoya_id == post.moyamoya_id).all()
            ]
            result.append({
                'id': post.moyamoya_id,
                'post': post.moyamoya_post,
                'user_id': post.post_user_id,
                'hash_tag': hashtags,
                'created_at': post.created_at.strftime("%Y-%m-%d %H:%M:%S") if post.created_at else None,
                'count': nice_count
            })
        
        return jsonify(result), 200
    
    return jsonify({"msg": "User not found"}), 404

# 保存した投稿の取得
@bp.route('/moyamoya_bookmark', methods=['GET'])
@jwt_required()
def moyamoya_bookmark():
    current_user = get_jwt_identity()
    
    if current_user:
        # ログインしているユーザーがブックマークした投稿IDを取得
        bookmark_posts = Bookmark.query.filter_by(user_id=current_user).all()
        bookmark_post_ids = [bookmark.post_id for bookmark in bookmark_posts]
        
        # ブックマークされた投稿IDに基づいて投稿を取得
        posts = Moyamoya.query.filter(Moyamoya.moyamoya_id.in_(bookmark_post_ids)).all()
        
        result = []
        
        for post in posts:
            nice_count = Nice.query.filter_by(post_id=post.moyamoya_id).count()
            
            # Moyamoya に関連付けられたハッシュタグを取得
            hashtags = [
                hashtag.tag_name
                for hashtag in HashTag.query.join(MoyamoyaHashtag).filter(MoyamoyaHashtag.moyamoya_id == post.moyamoya_id).all()
            ]
            result.append({
                'id': post.moyamoya_id,
                'post': post.moyamoya_post,
                'user_id': post.post_user_id,
                'hash_tag': hashtags,
                'created_at': post.created_at.strftime("%Y-%m-%d %H:%M:%S") if post.created_at else None,
                'count': nice_count
            })
        
        return jsonify(result), 200
    
    return jsonify({ 'message': 'Bookmark not found' }), 404

# 他者ユーザー投稿一覧
@bp.route('/user_post/<int:user_id>', methods=['GET'])
def user_post(user_id):
    user = User.query.get(user_id)
    
    if user:
        post = Moyamoya.query.filter_by(post_user_id=user.user_id).all()
        
        result = []
        
        for posts in post:
            nice_count = Nice.query.filter_by(post_id=posts.moyamoya_id).count()
            
            hashtags = [
                hashtag.tag_name
                for hashtag in HashTag.query.join(MoyamoyaHashtag).filter(MoyamoyaHashtag.moyamoya_id == post.moyamoya_id).all()
            ]
            result.append({
                'id': posts.moyamoya_id,
                'post': posts.moyamoya_post,
                'user_id': posts.post_user_id,
                'created_at': posts.created_at.strftime("%Y-%m-%d %H:%M:%S") if posts.created_at else None,
                'count': nice_count,
                'hashtag': hashtags
            })
        
        return jsonify(result),200
    
    else:
        return jsonify({ 'message': 'user not found' }),404

# 他者ユーザーのブックマーク一覧
@bp.route('/user_bookmark/<int:user_id>',methods=['GET'])
def user_bookmark(user_id):
    user = User.query.get(user_id)
    
    if user:
        user_bookmark = Bookmark.query.filter_by(user_id=user.user_id).all()
        bookmark_post_ids = [bookmark.post_id for bookmark in user_bookmark]
        
        posts = Moyamoya.query.filter(Moyamoya.moyamoya_id.in_(bookmark_post_ids)).all()
        
        result = []
        
        for post in posts:
            nice_count = Nice.query.filter_by(post_id=post.moyamoya_id).count()
            
            hashtags = [
                hashtag.tag_name
                for hashtag in HashTag.query.join(MoyamoyaHashtag).filter(MoyamoyaHashtag.moyamoya_id == post.moyamoya_id).all()
            ]
            result.append({
                'id': post.moyamoya_id,
                'post': post.moyamoya_post,
                'user_id': post.post_user_id,
                'created_at': post.created_at.strftime("%Y-%m-%d %H:%M:%S") if post.created_at else None,
                'count': nice_count,
                'hashtag': hashtags,
            })
        
        return jsonify(result),200
    else:
        return jsonify({'message':'Bookmark not found'}),404

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

# ハッシュタグに基づく投稿一覧取得
@bp.route('/hashtags/<string:hashtag>', methods=['GET'])
def get_hashtag_post(hashtag):
    try:
        # Moyamoya -> MoyamoyaHashtag -> HashTag のリレーションを使ってフィルタリング
        posts = Moyamoya.query.join(MoyamoyaHashtag).join(HashTag).filter(HashTag.tag_name == hashtag).all()
        result = []

        for post in posts:
            nice_count = Nice.query.filter_by(post_id=post.moyamoya_id).count()
            
            # Moyamoya に関連付けられたハッシュタグを取得
            hashtags = [
                hashtag.tag_name
                for hashtag in HashTag.query.join(MoyamoyaHashtag).filter(MoyamoyaHashtag.moyamoya_id == post.moyamoya_id).all()
            ]
            
            post_data = {
                'id': post.moyamoya_id,
                'post': post.moyamoya_post,
                'user_id': post.post_user_id,
                'tags': hashtags,  # ハッシュタグをリストで返す
                'created_at': post.created_at.strftime("%Y-%m-%d %H:%M:%S") if post.created_at else None,
                'count': nice_count,
            }
            result.append(post_data)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# トレンド機能
@bp.route('/hashtag_trend',methods=["GET"])
def trend():
    trends = get_trending_hashtags(db.session)
    return jsonify([{"tag": trend[0], "count": trend[1]} for trend in trends])


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
            "classification": pot.classification,
            "user_id": pot.pots_user_id,
            "created_at": pot.created_at.strftime("%Y-%m-%d %H:%M:%S") if pot.created_at else None,
        }
        pots_data.append(pot_data)
    return jsonify(pots_data), 200

# pots create
@bp.route('/pots',methods=['POST'])
@jwt_required()
def create_pots():
    current_user = get_jwt_identity()
    data = request.get_json()
    audio = data.get('audio')
    emotion = data.get('emotion')
    stress = data.get('stress')
    
    if audio and emotion and stress and current_user:
        pots = Pots(
            audio_file = audio,
            emotion_score = emotion,
            stress_level = stress,
            pots_user_id = current_user
        )
        db.session.add(pots)
        db.session.commit()
        return jsonify({
            'id': pots.pots_id,
            'audio_file': pots.audio_file,
            "emotion_score": pots.emotion_score,
            'stress': pots.stress_level,
            'user_id': pots.pots_user_id,
            'created_at': pots.created_at.strftime("%Y-%m-%d %H:%M:%S") if pots.created_at else None,
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

@bp.route('/audio', methods=['POST'])
@jwt_required()
def analyze_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    user = get_jwt_identity()
    audio_file = request.files['audio']
    audio_file_name = secure_filename(audio_file.filename)
    # ベースフォルダを指定してユーザーフォルダのパスを生成
    base_folder = current_app.config["UPLOAD_FOLDER_AUDIO"]
    user_folder = os.path.join(base_folder, str(user))
    os.makedirs(user_folder, exist_ok=True)  # フォルダが存在しない場合は作成

    # WebMファイルの保存パス
    webm_path = os.path.join(user_folder, audio_file_name)
    audio_file.save(webm_path)

    try:
        wav_filename = os.path.splitext(audio_file_name)[0] + ".wav"
        # WebMファイルをWAVに変換
        audio = AudioSegment.from_file(webm_path, format="webm")
        wav_path = os.path.join(current_app.config['UPLOAD_FOLDER_AUDIO'], wav_filename)
        audio.export(wav_path, format="wav")

        # WAVファイルをテキストに変換
        speech_text = transcribe_audio(wav_path)
        sentiment_result = analyze_sentiment(speech_text)
        
        # 感情分析結果を基にストレス発散方法を生成
        sugeestion = generate_stress_relief_suggestion(
            emotion=sentiment_result['classification'],
            text=speech_text,
        )
        
        pot = Pots(
            audio_file=audio_file_name,
            emotion_score = sentiment_result["predicted"],
            stress_level = sentiment_result["voltage"],
            classification = sentiment_result["classification"],
            pots_user_id = user,
            created_at = datetime.now()
        )
        
        db.session.add(pot)
        db.session.commit()
        
        # 主キーを含めたファイル名に更新し、user_folderに保存
        new_audio_file_name = f"{user}_{pot.pots_id}.webm"
        new_webm_path = os.path.join(user_folder, new_audio_file_name)
        os.rename(webm_path, new_webm_path)

        # オブジェクトのaudio_fileフィールドを更新
        pot.audio_file = new_audio_file_name
        db.session.commit()

        return jsonify({
            "text": speech_text,
            "classification": sentiment_result
        })
    except Exception as e:
        # エラー内容をサーバーログで確認
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# audiofile path
@bp.route('/audiofile/<user_id>/<filename>', methods=['GET'])
def audio_file(user_id, filename):
    # ユーザーフォルダのパスを指定
    user_folder = os.path.join(current_app.config['UPLOAD_FOLDER_AUDIO'], user_id)

    # ファイルが存在するか確認
    if not os.path.exists(os.path.join(user_folder, filename)):
        return jsonify({"error": "File not found"}), 404

    # ユーザーフォルダからファイルを送信
    return send_from_directory(user_folder, filename)


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
    # メッセージ生成
    context = f'{current_user_id.user_name}があなたをフォローしました'
    create_notifition(user_id,context)
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

@bp.route('/follow_type/<int:user_id>', methods=["GET"])
@jwt_required()
def follow_type(user_id):
    current_user = get_jwt_identity()
    
    follow_relation = Follow.query.filter_by(followed_user_id=user_id, follower_user_id=current_user).first()
    
    if follow_relation:
        return jsonify({"isFollower": True}), 200
    else:
        return jsonify({"isFollower": False}), 200


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

@socket.on('connect')
def handle_connect():
    try:
        # クエリパラメータからトークンを取得
        token = request.args.get('token')  # 'auth'ではなく、request.argsから取得
        if token:
            # トークンをデコードしてユーザーを確認
            decoded_token = decode_token(token)
            user_identity = decoded_token['sub']
        else:
            raise Exception('No token provided')
    except Exception as e:
        print(f'Connection failed: {str(e)}')
        disconnect()


@socket.on('send_message')
def handle_send_message(data):
    print(data)  # デバッグ用

    if 'group_id' in data and data['group_id']:  # グループIDが存在する場合のみグループチャット処理
        # グループチャットの場合
        group = GroupChat.query.get(data['group_id'])
        if not group:
            return  # グループが存在しない場合のエラーハンドリング
        new_message = Chats(
            message=data['message'],
            send_user_id=data['send_user_id'],
            group_id=data['group_id'],  # グループIDを設定
            chat_at=datetime.utcnow()
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        send_user = User.query.get(new_message.send_user_id)
        
        if send_user:
            group_member = GroupMember.query.filter_by(group_id=group.group_id).all()
            for member in group_member:
                if member.user_id != new_message.send_user_id:  # 送信者自身には通知を送らない
                    context = f'{send_user.user_name}がグループ「{group.group_name}」に新しいメッセージを送信しました'
                    create_notifition(member.user_id, context)
            db.session.commit()
    else:
        # 個人チャットの場合
        new_message = Chats(
            message=data['message'],
            send_user_id=data['send_user_id'],
            receiver_user_id=data['receiver_user_id'],
            chat_at=datetime.utcnow()
        )
    
        db.session.add(new_message)
        db.session.commit()
    
        send_user = User.query.get(new_message.send_user_id)
    
        # メッセージ生成
        if send_user:
            context = f'{send_user.user_name}があなたに新しいチャットを送信しました'
            create_notifition(new_message.receiver_user_id, context)
            db.session.commit()

    # メッセージ送信をクライアントに通知
    emit('receive_message', {
        'message': new_message.message,
        'sender': new_message.sender.user_name if new_message.sender else 'Unknown',
        'group': new_message.group.group_name if new_message.group else None,  # リレーションを使用
        'chat_at': new_message.chat_at.strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)



@bp.route('/chat_send', methods=['GET'])
@jwt_required()
def chat_send():
    current_user = get_jwt_identity()
    receiver_id = request.args.get('receiverId')

    if receiver_id:
        # 特定の相手ユーザーとの個人チャット履歴を取得
        user_chat = Chats.query.filter(
            ((Chats.send_user_id == current_user) & (Chats.receiver_user_id == receiver_id)) |
            ((Chats.send_user_id == receiver_id) & (Chats.receiver_user_id == current_user))
        ).order_by(Chats.chat_at.asc()).all()

        result = []
        for chat in user_chat:
            result.append({
                'message': chat.message,
                'timestamp': chat.chat_at.strftime('%Y-%m-%d %H:%M:%S'),
                'send_user_id': chat.send_user_id,
                'receiver_user_id': chat.receiver_user_id,
            })
        
        return jsonify(result), 200
    
    else:
        return jsonify({"error": "receiverId or groupId is required"}), 400


@bp.route('/chat_send_group', methods=['GET'])
@jwt_required()
def chat_send_group():
    group_id = request.args.get('group_id')
    
    if group_id:
        # グループチャットの履歴を取得し、送信者のユーザー情報を結合
        group_chat = db.session.query(Chats, User).join(User, Chats.send_user_id == User.user_id).filter(
            Chats.group_id == group_id
        ).order_by(Chats.chat_at.asc()).all()

        result = []
        for chat, user in group_chat:
            result.append({
                'message': chat.message,
                'timestamp': chat.chat_at.strftime('%Y-%m-%d %H:%M:%S'),
                'send_user_id': chat.send_user_id,
                'group_id': chat.group_id,  # グループIDを含める
                'sender_name': user.user_name,  # 送信者の名前
                'profile_image': user.prof_image  # 送信者のプロフィール画像
            })
        
        return jsonify(result), 200
    
    else:
        return jsonify({"error": "group_id is required"}), 400

# GroupChat作成
@bp.route('/group', methods=['POST'])
@jwt_required()
def create_group():
    current_user = get_jwt_identity()

    # フォームデータを受け取る
    group_name = request.form.get('group_name')  # JSONではなくformからデータを取得
    group_image = request.files.get('group_image')  # 画像ファイルを取得
    user_ids = request.form.getlist('user_ids[]')  # ユーザーIDのリストを取得

    if not group_name or not user_ids:
        return jsonify({'error': 'グループ名とメンバーは必須です。'}), 400
    
    # 画像がアップロードされた場合の処理
    if group_image:
        group_image_filename = secure_filename(group_image.filename)
        group_image.save(os.path.join(current_app.config['UPLOAD_FOLDER_GROUP'], group_image_filename))
    else:
        group_image_filename = None

    # グループ作成
    if group_name and current_user:
        new_group = GroupChat(group_name=group_name, create_by=current_user, group_image=group_image_filename)
        db.session.add(new_group)
        db.session.commit()

    # メンバー登録
    for user_id in user_ids:
        new_member = GroupMember(group_id=new_group.group_id, user_id=user_id)
        db.session.add(new_member)
    
    db.session.commit()

    return jsonify({'message': 'グループが作成されました。'}), 201

@bp.route('/groupchat',methods=['GET'])
@jwt_required()
def my_group():
    current_user = get_jwt_identity()
    
    user_group = db.session.query(GroupChat).join(GroupMember).filter(GroupMember.user_id == current_user).all()
    
    group_list = []
    
    for group in user_group:
        group_data = {
            'group_id': group.group_id,
            'group_name': group.group_name,
            'create_by': group.create_by,
            'create_at': group.create_at,
            'group_image': group.group_image,
        }
        group_list.append(group_data)
    
    return jsonify(group_list),200

@bp.route('/group_image/<filename>',methods=['GET'])
def group_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER_GROUP'],filename)
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
        db.session.commit()
        liked= False
        return jsonify({"liked": liked}),201
    else:
        # いいねしていない場合
        new_nice = Nice(post_id=post_id,user_id=current_user)
        db.session.add(new_nice)
        db.session.commit()
        liked=True
        return jsonify({"liked": liked}),200

# 特定のいいね取得
@bp.route('/nice/<int:post_id>', methods=['GET'])
@jwt_required()
def get_nice_status(post_id):
    current_user = get_jwt_identity()
    nice = Nice.query.filter_by(post_id=post_id, user_id=current_user).first()
    liked = nice is not None
    return jsonify({'liked': liked}),200


# Bookmark crudAPI

# create
@bp.route('/bookmark/<int:post_id>',methods=['POST'])
@jwt_required()
def bookmark(post_id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(post_id=post_id, user_id=current_user).first()

    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({'message': 'Bookmark removed'}), 200
    else:
        new_bookmark = Bookmark(post_id=post_id, user_id=current_user)
        db.session.add(new_bookmark)
        db.session.commit()
        return jsonify({'message': 'Bookmark added'}), 201

# user毎のbookmark取得
@bp.route('/bookmarks',methods=['GET'])
@jwt_required()
def bookmarks():
    current_user=get_jwt_identity()
    
    bookmarks = Bookmark.query.filter_by(user_id=current_user).all()
    
    bookmarks_post = [bookmark.post_id for bookmark in bookmarks]
    
    return jsonify({'bookmarks': bookmarks_post}),200


# notification crud

@bp.route('/notification',methods=['GET'])
@jwt_required()
def notification():
    current_user = get_jwt_identity()
    
    notification = Notification.query.filter_by(user_id=current_user).all()
    notification_data = []
    
    for noti in notification:
        notifications_data = {
            'id': noti.notification_id,
            'notification': noti.notification,
            'is_read': noti.is_read,
            'create_at': noti.create_at,
        }
        notification_data.append(notifications_data)
    
    return jsonify({'notification': notification_data}),200

@bp.route('/notification/unread',methods=["GET"])
@jwt_required()
def unread():
    current_user = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=current_user,is_read=False).all()
    return jsonify([{
            'id': noti.notification_id,
            'notification': noti.notification,
            'is_read': noti.is_read,
            'create_at': noti.create_at,}
            for noti in notifications
    ]),200

@bp.route('/notifications/mark-as-read/<int:notification_id>', methods=['POST'])
@jwt_required()
def mark_notification_as_read(notification_id):
    current_user = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user).first()
    if not notification:
        return jsonify({'error': '通知が見つかりません'}), 404
    
    notification.is_read = True
    db.session.commit()
    return jsonify({'message': '通知を既読にしました'})


@bp.route('/notifications/mark-all-as-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_as_read():
    current_user = get_jwt_identity()
    Notification.query.filter_by(user_id=current_user, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'すべての通知を既読にしました'})
