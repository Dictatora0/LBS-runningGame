

**作业说明文档**

**一、项目简介**

本项目是一个模拟“定向跑步夺冠”比赛的 Web API 系统，基于 Flask 和 SQLAlchemy 实现，使用 MySQL 作为后端数据库。支持创建多个比赛、添加运动员、提交实时位置、判断比赛结果、查询状态等功能。


**二、使用技术栈**

| **模块** | **技术说明**              |
| ------ | --------------------- |
| 后端框架   | Flask                 |
| ORM工具  | SQLAlchemy            |
| 数据库    | MySQL                 |
| 请求测试   | requests库 + 客户端脚本     |
| 可选前端   | HTML + JS（index.html） |

---

**三、API 接口设计与功能映射**

**1. 创建比赛**

• **URL**：POST /games

• **参数**（JSON）：

```
{
  "checkpoints": [
    {"x": 0.0, "y": 0.0},
    {"x": 5.0, "y": 5.0},
    {"x": 10.0, "y": 10.0}
  ]
}
```

• **功能**：创建包含检查点的游戏，返回新建的 game_id。

• **说明**：满足功能点 **②**

---

**2. 添加运动员**

• **URL**：POST /games/<game_id>/players

• **参数**（JSON）：

```
{
  "player_id": 1,
  "x": 0.0,
  "y": 0.0
}
```

• **功能**：向指定比赛中添加运动员，若重复添加则报错。

• **说明**：满足功能点 **③**

---

**3. 提交位置**

• **URL**：POST /games/<game_id>/players/<player_id>/location

• **参数**（JSON）：

```
{
  "x": 5.0,
  "y": 5.0
}
```

• **功能**：更新运动员在比赛中的位置，判断是否到达检查点或终点并记录成绩；若游戏已结束，则直接返回前三名结果。

• **说明**：满足功能点 **④** 和 **⑦**

---

**4. 获取检查点**

• **URL**：GET /games/<game_id>/checkpoints

• **返回**：

```
{
  "status": "已结束" | "未结束",
  "checkpoints": [{"x": ..., "y": ...}, ...]
}
```

• **功能**：返回比赛的所有检查点坐标及当前状态。

• **说明**：满足功能点 **⑤**

---

**5. 获取游戏状态**

• **URL**：GET /games/<game_id>/status

• **返回**：

```
{
  "status": "已结束" | "未结束",
  "champion": 1,
  "runner_up": 2,
  "third_place": 3
}
```

• **功能**：查询游戏当前状态及比赛前三名选手。

• **说明**：满足功能点 **⑥**

---

**6. 删除游戏**

• **URL**：DELETE /games/<game_id>

• **功能**：用于清除无用比赛数据，防止数据库堆积。

---

**四、数据库设计说明**

**表结构一览：**

**games 表**

| **字段名**     | **类型**  | **说明**               |
| ----------- | ------- | -------------------- |
| game_id     | Integer | 主键，自增                |
| status      | Enum    | 状态（ongoing/finished） |
| champion    | Integer | 冠军ID                 |
| runner_up   | Integer | 亚军ID                 |
| third_place | Integer | 季军ID                 |

**checkpoints 表**

| **字段名**       | **类型**  | **说明**  |
| ------------- | ------- | ------- |
| checkpoint_id | Integer | 主键，自增   |
| game_id       | Integer | 外键，关联比赛 |
| x, y          | Float   | 坐标点     |

**players 表**

| **字段名**         | **类型**   | **说明** |
| --------------- | -------- | ------ |
| player_id       | Integer  | 主键（复合） |
| game_id         | Integer  | 主键（复合） |
| x, y            | Float    | 实时位置坐标 |
| reached         | Integer  | 到达检查点数 |
| finished        | Boolean  | 是否完成比赛 |
| submission_time | DateTime | 提交时间戳  |

---

**五、运行说明**

**🛠️ 安装依赖：**

```
pip install -r requirements.txt
```

**🚀 启动 Flask 服务：**

```
python /Users/lifulin/Desktop/running_game_api/Game/app.py
```

默认启动在 http://localhost:5000。

**🧪 运行客户端测试脚本：**

```
python /Users/lifulin/Desktop/client_test.py
```

也可以使用 Postman/Web 页面测试。

---

**六、测试截图/演示页面**


---

**七、功能实现情况说明**

| **功能点**         | **是否完成** | **说明**              |
| --------------- | -------- | ------------------- |
| 1. 支持多个游戏       | ✅        | game_id 区分多个比赛      |
| 2. 创建比赛         | ✅        | 支持创建、分配 game_id     |
| 3. 添加运动员        | ✅        | 重复添加返回报错            |
| 4. 提交位置 / 判断前三名 | ✅        | 包含距离判断和时间排序         |
| 5. 查询途经点和状态     | ✅        | 状态和坐标都返回            |
| 6. 查询是否结束       | ✅        | 有状态字段，返回前三名         |
| 7. 比赛结束通知       | ✅（被动返回）  | 在每次位置更新中自动判断是否结束并告知 |
