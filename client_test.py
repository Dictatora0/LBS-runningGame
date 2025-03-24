import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def create_game():
    print("== 创建比赛 ==")
    checkpoints = [
        {"x": 0.0, "y": 0.0},
        {"x": 5.0, "y": 5.0},
        {"x": 10.0, "y": 10.0}
    ]
    res = requests.post(f"{BASE_URL}/games", json={"checkpoints": checkpoints})
    print("返回：", res.text)
    try:
        data = res.json()
        return data.get("game_id")
    except Exception as e:
        print("解析 JSON 失败:", e)
        print("状态码:", res.status_code)
        print("响应头:", res.headers)
        print("响应体:", repr(res.text))
        return None

def add_player(game_id, player_id, x, y):
    print(f"== 添加运动员 {player_id} ==")
    res = requests.post(f"{BASE_URL}/games/{game_id}/players", json={
        "player_id": player_id,
        "x": x,
        "y": y
    })
    print("返回：", res.text)

def submit_location(game_id, player_id, x, y):
    print(f"== 提交位置 (player {player_id} @ {x},{y}) ==")
    res = requests.post(f"{BASE_URL}/games/{game_id}/players/{player_id}/location", json={
        "x": x,
        "y": y
    })
    print("返回：", res.text)

def get_checkpoints(game_id):
    print("== 查询检查点 ==")
    res = requests.get(f"{BASE_URL}/games/{game_id}/checkpoints")
    print("返回：", res.text)

def get_status(game_id):
    print("== 查询比赛状态 ==")
    res = requests.get(f"{BASE_URL}/games/{game_id}/status")
    print("返回：", res.text)

def delete_game(game_id):
    print("== 删除比赛 ==")
    res = requests.delete(f"{BASE_URL}/games/{game_id}")
    print("返回：", res.text)

def simulate_game():
    # 1. 创建游戏
    game_id = create_game()
    if not game_id:
        print("游戏创建失败，退出测试")
        return
    time.sleep(1)

    # 2. 添加选手
    for pid in [101, 102, 103]:
        add_player(game_id, pid, 0.0, 0.0)
        time.sleep(0.5)

    # 3. 模拟选手依次移动通过检查点
    checkpoints = [(5.0, 5.0), (10.0, 10.0)]
    for pid in [101, 102, 103]:
        for pos in checkpoints:
            submit_location(game_id, pid, pos[0], pos[1])
            time.sleep(0.5)

    # 4. 查询检查点信息
    get_checkpoints(game_id)
    time.sleep(0.5)

    # 5. 查询比赛状态
    get_status(game_id)
    time.sleep(0.5)

    # 6. 删除比赛
    delete_game(game_id)

if __name__ == '__main__':
    simulate_game()