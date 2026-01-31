# 内网微型任务管理系统 - 技术实施方案书 (v2.1)

**版本**: 2.1  
**适用场景**: 局域网内网环境 / Windows 桌面办公  
**核心目标**: 极简任务分发与统计、结构化周报管理、零干扰桌面挂件  
**最后更新日期**: 2026-01-31

## 1. 系统架构 (Architecture)

采用 C/S 架构，服务端容器化部署，客户端分发独立可执行文件。

### 服务端 (Server):
*   **Runtime**: Python 3.10+ (FastAPI)
*   **Database**: PostgreSQL 15 (Docker 部署)
*   **ORM**: Tortoise-ORM / SQLAlchemy (Async)
*   **OS**: Windows (作为服务器) 或 x86 Linux Server
*   **Auth**: JWT (JSON Web Tokens) with long expiration for auto-login.

### 客户端 (Client):
*   **Core**: Tauri v2 (Rust + Webview)
*   **Frontend**: Vue 3 + TypeScript + Ant Design Vue
*   **Charts**: Apache ECharts
*   **Form Factor**: 
    *   主界面：正常窗口
    *   **挂件**: 半透明贴条常驻桌面 (Semi-transparent Sticky Note widget)，极简显示当前待办。

### 网络 (Network):
*   服务端配置固定局域网 IP (如 192.168.1.200)
*   端口开放: API (8000), DB (5432, 可选)
*   **通信机制**: 轮询 (Polling) 或 长轮询 (Long Polling)。由于数据频次低，初始采用短轮询 (如 30s-60s) 即可满足需求。

## 2. 详细功能模块 (Functional Modules)

### 2.1 用户与权限管理 (User Admin)
*仅管理员可见*

*   **账号全生命周期管理**:
    *   **新建**: 设置 username, display_name, role (Admin/Employee), initial_password.
    *   **编辑**: 修改显示名称、所属分组。
    *   **禁用**: 离职处理。将 `is_active` 置为 false，保留历史数据但禁止登录。
    *   **密码重置**: 强制重置用户密码。
*   **认证与安全**: 
    *   密码存库使用 bcrypt/argon2 Hash。
    *   **自动登录**: 除非手动退出，否则保持长期登录状态 (Long-lived JWT or Refresh Token flow)。

### 2.2 任务管理系统 (Task System)
*核心业务逻辑*

*   **任务分发 (Distribution)**:
    *   **单发**: 选择单个用户分配。
    *   **群发 (Batch)**: 选择“全员”或“多选”。
    *   **性能优化**: 群发时使用 ORM 的 `bulk_create` 批量插入，避免循环写入导致延迟。
    *   **裂变逻辑**: 保持每人一条独立 Task 记录，通过 `batch_id` 关联。
*   **状态流转**:
    *   `Pending` -> `Done`。
    *   **打勾即完成**: 桌面挂件或主界面勾选即触发请求。
    *   **时间戳**: 服务端写入 `completed_at`。

### 2.3 周报管理系统 (Weekly Reports)
*   **结构化数据**:
*   **填写格式 (三段式)**:
    1.  本周工作内容 (Work Done)
    2.  下周计划 (Next Week Plan)
    3.  问题与风险 (Issues & Risks)
*   **展示优化**: 前端支持简单的 Markdown 渲染或自动列表格式化，优化管理员大屏阅读体验。
*   **约束条件**:
    *   **零文件**: 禁止附件。
    *   **截止判定**: 服务端判定 `is_late`。

### 2.4 运维与更新 (Ops)
*   **版本检测**:
    *   服务端提供静态文件服务 (`GET /static/version.json` & `/static/client-latest.exe`)。
    *   客户端启动时请求 API 获取版本信息。
*   **交互**: 发现新版本时弹窗提示，并可直接调用浏览器或内置下载器从 HTTP 服务下载更新 (避开 SMB 共享权限问题)。

## 3. 数据库设计 (Database Schema)

### A. System Settings (系统配置)
*   (保持不变)

### B. Users (用户)
*   (保持不变)

### C. Tasks (任务)
*   (保持不变)

### D. Reports (周报)
*   (保持不变)

## 4. 统计大屏逻辑 (Dashboard Logic)
*管理员端通过 ECharts 展示*

1.  **工时热力图 (Activity Heatmap)**: 分析 `Tasks.completed_at`。
2.  **周报合规看板 (Compliance)**: 统计提交/迟交/未交。
3.  **任务响应效率 (Response Time)**: `Avg(completed_at - created_at)`。

## 5. 部署结构 (Directory Structure)

```text
/internal-task-system
├── docker-compose.yml          # 编排 API (FastAPI) 和 DB (Postgres)
├── /backend                    # FastAPI 项目
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── /static                 # 存放 version.json 和 .exe (HTTP Serve)
│   └── Dockerfile
├── /pgdata                     # Postgres 数据持久化挂载
└── /client-source              # Tauri 源码 (开发环境)
```

## 6. 开发路线图 (Roadmap)

### Phase 1: MVP (最小可用版)
*   [ ] 搭建 Docker 环境 (Postgres + FastAPI)。
*   [ ] 实现 API: Auth(JWT), Tasks(Batch w/ bulk_create), Reports, Static Serve。
*   [ ] 开发客户端: 
    *   **桌面挂件**: 实现半透明、无边框、置顶窗口 (Tauri Window Configuration)。
    *   **通知**: 基于轮询的任务刷新。
*   [ ] **交付物**: 局域网内可运行，员工通过桌面贴条接收任务。

### Phase 2: Admin Power (管理增强)
*   [ ] 开发管理员前端: 大屏 Layout + Markdown 渲染周报。
*   [ ] 实现用户管理模块。
*   [ ] 实现任务群发撤回 (Batch Delete)。
*   [ ] **交付物**: 管理员自主维护。

### Phase 3: Insight & Ops (统计与运维)
*   [ ] ECharts 统计集成。
*   [ ] 客户端 HTTP 自动/手动更新流程。
*   [ ] **交付物**: 完整版 v1.0。
