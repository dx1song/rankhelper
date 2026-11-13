# 无畏契约上分辅导（Valorant 排位辅导 Web 应用）

## 技术栈

- 后端：FastAPI + SQLModel + PostgreSQL（api/ services/ models/ schemas/ 分层）
- 前端：React + TypeScript + Vite + Tailwind + shadcn/ui，图表用 Recharts
- AI：DeepSeek V4 Pro（OpenAI 兼容接口）
- 数据源：HenrikDev Valorant API
- 部署：Docker Compose 本地开发

## 启动

1. 准备环境变量：

   ```bash
   cp backend/.env.example backend/.env
   # 填入 HENRIK_API_KEY、DEEPSEEK_API_KEY
   ```

2. 启动全部服务：

   ```bash
   docker compose up --build
   ```

   - 后端：http://localhost:8000 （健康检查 /health）
   - 前端：http://localhost:5173
   - 数据库：localhost:5432

## 当前状态

项目骨架阶段：目录分层、路由占位、SQLModel 建表已就位，所有业务接口返回 501，业务逻辑待逐个模块实现。
