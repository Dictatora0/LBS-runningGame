from flask import Flask, request, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
import math
from sqlalchemy.exc import SQLAlchemyError
from threading import Lock

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/lbsApi'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
lock = Lock()  # 线程锁，防止并发问题

class Game(db.Model):
    __tablename__ = 'games'
    game_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum('ongoing', 'finished'), default='ongoing', nullable=False)
    champion = db.Column(db.Integer, nullable=True)
    runner_up = db.Column(db.Integer, nullable=True)
    third_place = db.Column(db.Integer, nullable=True)


class Checkpoint(db.Model):
    __tablename__ = 'checkpoints'
    checkpoint_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)

class Player(db.Model):
    __tablename__ = 'players'
    player_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), primary_key=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    reached = db.Column(db.Integer, default=0)  # 通过的检查点数
    finished = db.Column(db.Boolean, default=False)
    submission_time = db.Column(db.DateTime, default=db.func.current_timestamp())

# 计算两点距离
def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# 首页
@app.route('/')
def index():
    return render_template('index.html')


# 1. 创建比赛
@app.route('/games', methods=['POST'])
def create_game():
    data = request.json
    checkpoints = data.get('checkpoints', [])

    if len(checkpoints) < 3:
        return jsonify({'error': '必须至少有3个检查点'}), 400
    
    try:
        new_game = Game()
        db.session.add(new_game)
        db.session.flush()  # 让 new_game 获取 game_id

        db.session.bulk_insert_mappings(Checkpoint, [
            {'game_id': new_game.game_id, 'x': cp['x'], 'y': cp['y']} for cp in checkpoints
        ])
        db.session.commit()
        return jsonify({'game_id': new_game.game_id, 'message': 'Game created successfully'}), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '数据库错误'}), 500


# 2. 添加运动员
@app.route('/games/<int:game_id>/players', methods=['POST'])
def add_player(game_id):
    data = request.json
    player_id = data.get('player_id')

    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': '比赛不存在'}), 404
    if game.status == 'finished':
        return jsonify({'error': '比赛已结束，无法添加运动员'}), 400

    if Player.query.filter_by(game_id=game_id, player_id=player_id).first():
        return jsonify({'error': '运动员已存在'}), 400

    try:
        new_player = Player(player_id=player_id, game_id=game_id, x=data['x'], y=data['y'])
        db.session.add(new_player)
        db.session.commit()
        return jsonify({'message': 'Player added successfully'}), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '数据库错误'}), 500

# 3. 提交位置
@app.route('/games/<int:game_id>/players/<int:player_id>/location', methods=['POST'])
def update_location(game_id, player_id):
    data = request.json
    player = Player.query.filter_by(game_id=game_id, player_id=player_id).first()
    game = Game.query.get(game_id)

    if not player:
        return jsonify({'error': '运动员未找到'}), 404
    if game.status == 'finished':
        return jsonify({'message': '游戏已结束', 'champion': game.champion, 'runner_up': game.runner_up, 'third_place': game.third_place}), 200

    player.x, player.y = data['x'], data['y']
    
    checkpoints = Checkpoint.query.filter_by(game_id=game_id).all()
    if player.reached < len(checkpoints) and distance(player.x, player.y, checkpoints[player.reached].x, checkpoints[player.reached].y) < 2.0:
        player.reached += 1

    if player.reached == len(checkpoints):  
        player.finished = True
        db.session.commit()
        
        finished_players = Player.query.filter_by(game_id=game_id, finished=True).order_by(Player.submission_time).limit(3).all()
        if len(finished_players) == 3:
            game.champion, game.runner_up, game.third_place = [p.player_id for p in finished_players]
            game.status = 'finished'
    
    db.session.commit()
    return jsonify({'message': 'Location updated successfully'}), 200

# 4. 获取检查点
@app.route('/games/<int:game_id>/checkpoints', methods=['GET'])
def get_checkpoints(game_id):
    game = Game.query.get(game_id)
    checkpoints = Checkpoint.query.filter_by(game_id=game_id).all()

    return jsonify({
        'status': '已结束' if game.status == 'finished' else '未结束',
        'checkpoints': [{'x': c.x, 'y': c.y} for c in checkpoints]
    }), 200


# 5. 获取游戏状态
@app.route('/games/<int:game_id>/status', methods=['GET'])
def get_game_status(game_id):
    game = Game.query.get(game_id)
    return jsonify({
        'status': '已结束' if game.status == 'finished' else '未结束',
        'champion': game.champion,
        'runner_up': game.runner_up,
        'third_place': game.third_place
    }), 200

# 6. 删除游戏（防止数据库堆积无用比赛）
@app.route('/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    game = Game.query.get(game_id)
    if not game:
        return jsonify({'error': '游戏不存在'}), 404

    try:
        db.session.delete(game)
        db.session.commit()
        return jsonify({'message': 'Game deleted successfully'}), 200
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '删除失败'}), 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)