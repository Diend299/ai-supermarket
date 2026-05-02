# AI Supermarket 启动指南

## 1. 数据库准备

首先确保MySQL已安装并运行，然后执行schema.sql文件创建数据库和表：

```bash
mysql -u root -p < schema.sql
```

或者手动在MySQL中执行schema.sql的内容。

注意：默认数据库配置在backend-java/demo/src/main/resources/application.yaml中：
- 数据库名：aip_db
- 用户名：root
- 密码：root123456

如需修改，请更新application.yaml文件。

## 2. 后端启动

进入backend-java/demo目录，使用Maven启动Spring Boot：

```bash
cd backend-java/demo
mvn spring-boot:run
```

或在IDEA中直接运行DemoApplication.java

后端将在 http://localhost:8080 启动

## 3. 前端启动

在另一个终端中，进入frontend-vue目录：

```bash
cd frontend-vue
npm install
npm run dev
```

前端将在 http://localhost:5173 启动

## 4. 访问系统

打开浏览器访问 http://localhost:5173

- 首次使用请点击"立即注册"创建账号
- 注册成功后使用账号密码登录
- 登录成功后进入首页

## 项目结构

### 后端 (Spring Boot)
- controller: 控制器层 (AuthController)
- service: 服务层 (UserService)
- mapper: 数据访问层 (UserMapper)
- entity: 实体类 (User)
- dto: 数据传输对象
- config: 配置类 (SecurityConfig, JwtUtil)

### 前端 (Vue 3 + TypeScript)
- views: 页面组件 (Login, Register, Home)
- router: 路由配置
- store: 状态管理 (Pinia)
- api: API接口封装
- utils: 工具函数 (axios封装)

## API文档

后端启动后，可访问 Swagger API 文档：
http://localhost:8080/swagger-ui/index.html
