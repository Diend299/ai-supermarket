# 🏪 AI Supermarket — 多Agent协同式AI企业运营平台

> **让AI像超市一样触手可及** — 开箱即用的一站式AI内容创作平台

---

## 📦 项目简介

本项目是一个基于 **Spring Boot + Vue 3 + Python AI Worker** 的一站式AI内容创作平台，核心功能包括：

- ✅ **AI文案创作** 🎯 — 输入主题，调用 DeepSeek API 自动生成营销文案（text2text）
- ✅ **语音合成（TTS）** 🎤 — 将文本转化为自然语音，支持多种语音风格
- ✅ **数字人视频生成** 👤 — 使用 Wav2Lip 技术，上传音频驱动数字人生成视频
- ✅ **头像/形象生成** 🖼️ — AI 生成数字人形象
- ✅ **任务队列** ⏳ — 基于 Redis 的异步任务处理，提交即返回
- ✅ **实时推送** 🔄 — SSE 实时推送任务进度，无需手动刷新
- ✅ **用户系统** 🔐 — 注册登录 + JWT 鉴权
- ✅ **API 文档** 📋 — 符合 OpenAPI 3.0 规范，支持导入 Apifox 等工具

---

## 🏗️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 🖥️ **后端** | Java 17 + Spring Boot 3.x | REST API、鉴权、任务管理、SSE推送 |
| 🗄️ **数据库** | MySQL 8.0 | 用户数据、任务记录、生成结果 |
| ⚡ **缓存/队列** | Redis 7 | 任务队列 + 消息通知（Pub/Sub）|
| 🎨 **前端** | Vue 3 + TypeScript + Vite + Element Plus | 用户界面 |
| 🤖 **AI Worker** | Python 3.11+ | 调用 DeepSeek API、GPT-SoVITS、Wav2Lip |
| 🐳 **部署** | Docker / Docker Compose | 一键启动基础设施 |
| 📋 **API 文档** | OpenAPI 3.0 (JSON) | 导入 Apifox 调试接口 |

---

## 🚀 快速开始（小白友好版）

> **只需要 4 步，就能跑起来！** 🎉

### 准备工作

| 软件 | 版本要求 | 下载地址 |
|------|----------|----------|
| **Docker Desktop** | 最新版 | https://www.docker.com/products/docker-desktop/ |
| **Node.js** | >= 20.19.0 | https://nodejs.org/ |
| **Java** | 17+ | https://adoptium.net/ |
| **Maven** | 3.8+ | https://maven.apache.org/download.cgi |
| **Python** | 3.11+ | https://www.python.org/downloads/ |
| **DeepSeek API Key** | 必填 | https://platform.deepseek.com/ |

---

### 第 1 步：启动 MySQL + Redis（用 Docker 一键搞定！）

打开终端（CMD 或 PowerShell），**cd 到项目目录**，然后执行：

```bash
# 启动 MySQL 和 Redis（后台运行）
docker-compose up -d
```

> ⏳ 第一次运行会下载镜像，需要等几分钟。完成后验证：

```bash
# 查看容器是否正常运行
docker ps

# 应该看到两个容器：
# ai-supermarket-mysql  （端口 3306）
# ai-supermarket-redis  （端口 6379）
```

> 🔥 **搞定！** MySQL 和 Redis 已经跑起来了。
> - MySQL 会自动创建 `ai_supermarket` 数据库并导入建表脚本
> - 连接信息：`root / root123456`

---

### 第 2 步：启动后端（Java Spring Boot）

```bash
# 进入后端目录
cd backend-java/demo

# 下载依赖并启动（第一次运行需要下载，可能较慢）
mvn spring-boot:run
```

> ✅ 启动成功看到 `Started DemoApplication` 即说明后端已在 **http://localhost:8080** 运行。

> 💡 **不需要修改任何配置！** 默认连接本地的 MySQL 和 Redis（就是上面 Docker 启动的）

---

### 第 3 步：启动前端（Vue 3）

**新开一个终端**，执行：

```bash
# 进入前端目录
cd frontend-vue

# 安装依赖（仅第一次需要）
npm install

# 启动开发服务器
npm run dev
```

> ✅ 启动成功后在浏览器打开 **http://localhost:5173**

---

### 第 4 步：配置并启动 AI Worker（Python 文本生成服务）

**再新开一个终端**，执行：

```bash
# 进入 AI Worker 目录
cd ai-worker

# 安装 Python 依赖
pip install -r requirements.txt

# 配置 DeepSeek API Key（用文本编辑器打开 .env 文件）
# 找到 DEEPSEEK_API_KEY= 这一行，填入你的 Key
# 例如：DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 启动 Worker
python main.py
```

> ✅ 看到 `"AI Worker 启动"` 字样即说明 Worker 已就绪，等待任务。

> 💡 **DeepSeek API Key 在哪获取？**
> 1. 访问 https://platform.deepseek.com/
> 2. 注册账号 → 进入 API Keys 页面
> 3. 创建一个新的 API Key，复制后粘贴到 `ai-worker/.env` 文件中

---

## 🎯 使用指南

启动全部服务后，打开浏览器访问 **http://localhost:5173**

### 1️⃣ 注册账号
![](https://via.placeholder.com/600x300?text=注册页面)

- 点击「立即注册」创建账号
- 用户名 + 密码即可注册

### 2️⃣ 登录系统
- 输入刚注册的账号密码登录

### 3️⃣ 开始文案创作
- 在左侧导航栏点击 **「数字人」👤** 旁的 **「文案创作」**
- 或者从首页快捷操作中点击 **「文案创作」📝**
- 输入文案主题（例如：*写一篇618大促活动推广文案*）
- 可选：补充风格要求（如：*风格活泼、500字左右*）
- 点击「开始创作」🚀
- **等待几秒钟**，AI 自动生成文案并展示 👇

### 4️⃣ 查看结果
- 生成成功后，结果会直接显示在页面上
- 点击「复制文案」可一键复制
- 历史记录在右侧面板查看

---

## 📁 项目结构

```
ai-supermarket/
│
├── docker-compose.yml          # Docker 一键启动 MySQL + Redis
├── schema.sql                  # 数据库建表脚本
├── README.md                   # 📄 本文件（使用说明）
│
├── backend-java/demo/          # 🖥️ Java 后端（Spring Boot）
│   ├── pom.xml
│   └── src/main/java/com/example/demo/
│       ├── controller/         # REST 接口层
│       ├── service/            # 业务逻辑层
│       ├── mapper/             # 数据访问层（MyBatis）
│       ├── entity/             # 数据库实体
│       ├── dto/                # 数据传输对象
│       ├── config/             # 配置（JWT、Redis、安全）
│       └── util/               # 工具类
│
├── frontend-vue/               # 🎨 前端（Vue 3 + TypeScript）
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── api/                # API 封装
│   │   ├── router/             # 路由
│   │   ├── store/              # 状态管理
│   │   └── utils/              # 工具函数
│   └── package.json
│
├── api-docs.json               # 📋 OpenAPI 3.0 规范文件（可导入 Apifox）
│
├── ai-worker/                  # 🤖 AI Worker（Python）
│   ├── main.py                 # 主循环（任务分发）
│   ├── config.py               # 配置文件
│   ├── db.py                   # 数据库操作
│   ├── redis_client.py         # Redis 队列操作
│   ├── .env                    # ⚠️ 环境变量（API Key 等）
│   ├── requirements.txt        # Python 依赖
│   ├── text2text/              # 📝 文生文模块 — 调用 DeepSeek API
│   │   ├── __init__.py
│   │   └── test.py
│   ├── tts_generate/           # 🎤 语音合成模块 — GPT-SoVITS
│   │   ├── __init__.py
│   │   └── process.py
│   ├── wav2lip_generate/       # 👤 数字人生成模块 — Wav2Lip
│   │   ├── __init__.py
│   │   └── process.py
│   ├── avatar_generate/        # 🖼️ 头像生成模块
│   │   ├── __init__.py
│   │   └── process.py
│   └── avatar/                 # 数字人模型数据
│
└── .task_progress.md           # 开发进度（可忽略）
```

---

## 📋 API 文档（Apifox 导入说明）

项目根目录下的 [`api-docs.json`](./api-docs.json) 是符合 **OpenAPI 3.0** 规范的 API 文档文件，可以直接导入 [Apifox](https://apifox.com/) 等 API 调试工具。

### 接口总览

| 分组 | 路径 | 方法 | 说明 |
|------|------|------|------|
| 🔐 **用户认证** | `/api/auth/register` | POST | 用户注册 |
| | `/api/auth/login` | POST | 用户登录，返回 JWT Token |
| 🤖 **AI任务管理** | `/api/task/create` | POST | 创建AI生成任务 |
| | `/api/task/list` | GET | 获取用户的任务列表 |
| | `/api/task/{taskId}` | GET | 查询任务进度/详情 |
| | `/api/task/{taskId}/result` | GET | 获取任务结果资源 |
| | `/api/task/{taskId}/subscribe` | GET | SSE 订阅任务状态（实时推送）|
| 👤 **数字人管理** | `/api/avatar/list` | GET | 获取可用数字人列表 |
| 📁 **文件上传** | `/api/upload/audio` | POST | 上传音频文件（wav/mp3）|

### 导入 Apifox

1. 打开 Apifox，点击 **「导入」→「OpenAPI / Swagger」**
2. 选择 **「文件导入」**，选中项目根目录的 `api-docs.json`
3. 点击 **「确定」** 完成导入
4. 导入后会自动生成所有接口，可直接在线调试

### 通用接口规范

- **基础地址**: `http://localhost:8080`
- **响应格式**: 统一 JSON 包裹
  ```json
  { "code": 0, "msg": "success", "data": { ... } }
  ```
- **鉴权方式**: Bearer JWT Token（`Authorization: Bearer <token>`）
- **任务状态码**: `0`=排队中, `1`=生成中, `2`=成功, `3`=失败

---

## ⚠️ 常见问题（FAQ）

### ❓ Docker 启动失败？
- **确保 Docker Desktop 已安装并运行**（系统托盘能看到鲸鱼图标 🐳）
- Windows 用户可能需要启用 WSL2
- 尝试重启 Docker Desktop 后再试

### ❓ Maven 下载很慢？
- 第一次运行需要下载大量依赖，请耐心等待
- 或者配置阿里云镜像加速（百度搜索 "Maven 阿里云镜像"）

### ❓ npm install 报错？
- 确保 Node.js 版本 >= 20.19.0
- 可以试试删除 `node_modules` 文件夹重新安装

### ❓ 前端连接不上后端？
- 确认后端是否在 http://localhost:8080 运行
- 检查 `frontend-vue/src/views/Copywriting.vue` 中的 `VITE_API_BASE_URL` 配置

### ❓ AI Worker 报错 "API Key 未配置"？
- 打开 `ai-worker/.env` 文件
- 把 `DEEPSEEK_API_KEY=your_deepseek_api_key` 改成你的真实 Key

### ❓ 文案生成为空或报错？
- 检查 DeepSeek API Key 是否有效（余额是否充足）
- 检查 `ai-worker` 终端是否有错误日志

---

## 🔧 常用命令速查

```bash
# ----- Docker -----
docker-compose up -d            # 启动 MySQL + Redis
docker-compose down             # 停止并删除容器
docker-compose logs -f mysql    # 查看 MySQL 日志
docker-compose restart redis    # 重启 Redis

# ----- 后端 -----
cd backend-java/demo
mvn spring-boot:run             # 启动后端（开发模式）
mvn package -DskipTests         # 打包后端 JAR（生成 target/demo-0.0.1-SNAPSHOT.jar）

# ----- 前端 -----
cd frontend-vue
npm run dev                     # 启动前端（开发模式）
npm run build                   # 打包前端（生产模式，生成 dist/ 文件夹）

# ----- AI Worker -----
cd ai-worker
python main.py                  # 启动 Worker

# ----- Git -----
git push origin feature/添加文生文功能（基于DeepSeekAPI）  # 上传代码
```

---

## 💡 小贴士

- 🟢 **每次开机后**，只需要先执行 `docker-compose up -d`，然后依次启动后端、前端、AI Worker
- 🔄 如果修改了代码，后端需要重启才能生效（Ctrl+C 停止，重新 `mvn spring-boot:run`）
- 🐍 AI Worker 修改后也需要重启（Ctrl+C 停止，重新 `python main.py`）
- 🌐 前端热更新，修改代码后浏览器会自动刷新，**无需重启**

---

## 📄 许可证

MIT License
