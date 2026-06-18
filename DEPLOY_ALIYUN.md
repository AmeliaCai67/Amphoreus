# Amphoreus 永劫回归模拟器 - 阿里云 ECS 部署方案

## 一、现有资源盘点

| 项目 | 配置 |
|------|------|
| 实例 | iZbp1ii2ts9plycd758snlZ |
| 地域 | 华东1（杭州） |
| 公网 IP | 47.99.201.66 |
| 规格 | ecs.e-c1m1.large（2 vCPU / 2 GiB） |
| 系统 | Ubuntu 22.04 64位 |
| 到期 | 2027-03-29 |
| 付费 | 包年包月 |

> ⚠️ **容量提示**：2核2G 对于 Docker 全量部署较为紧张。本方案采用「Nginx 托管前端静态文件 + Systemd 托管 Python 后端」的混合模式，比纯 Docker 节省约 500MB-1GB 内存。

---

## 二、部署架构

```
用户浏览器
     │
     ▼
[ 阿里云安全组 :80 / :443 ]
     │
     ▼
[ Nginx 反向代理 ]  ← 监听 80/443，托管前端静态文件
     │
     ├─ /  → 前端 dist 目录（Vue 构建产物）
     └─ /api/ → 反向代理到 localhost:8000
                    │
                    ▼
            [ Python FastAPI ] ← Systemd 守护进程
                    │
                    ▼
            [ DeepSeek / InternLM / MiniMax API ]
```

---

## 三、环境准备（SSH 登录后执行）

### 3.1 基础依赖安装

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y git curl wget nginx build-essential python3-pip python3-venv

# 安装 Node.js 20（用于前端构建）
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 验证版本
python3 --version  # 应 >= 3.10
node --version     # 应 >= 20
npm --version
nginx -v
```

### 3.2 配置时区

```bash
sudo timedatectl set-timezone Asia/Shanghai
```

---

## 四、代码部署

### 4.1 克隆项目

```bash
cd /var/www
git clone https://github.com/your-repo/Amphoreus.git amphoreus
# 或直接从本地上传：scp -r ./Amphoreus root@47.99.201.66:/var/www/amphoreus
cd amphoreus
```

### 4.2 后端环境配置

```bash
cd /var/www/amphoreus

# 创建 Python 虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖（去除开发依赖以节省空间）
pip install --no-cache-dir -r requirements.txt

# 创建 .env 文件（务必修改为你的真实密钥）
cat > .env << 'EOF'
# DeepSeek API（主要使用）
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# InternLM API（可选）
INTERN_API_KEY=your_intern_api_key_here
INTERN_BASE_URL=https://chat.intern-ai.org.cn/api/v1
INTERN_MODEL=internlm3-latest

# MiniMax API（可选）
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M1
EOF

chmod 600 .env
```

### 4.3 前端构建

```bash
cd /var/www/amphoreus/frontend

# 安装依赖并构建
npm install
npm run build

# 构建产物位于 frontend/dist/，后续由 Nginx 直接托管
```

---

## 五、Nginx 配置（核心）

### 5.1 覆盖默认配置

```bash
sudo tee /etc/nginx/sites-available/amphoreus > /dev/null << 'EOF'
server {
    listen 80;
    server_name 47.99.201.66;  # 后续如有域名，替换此处

    # 前端静态文件
    location / {
        root /var/www/amphoreus/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;  # 支持 Vue Router History 模式
    }

    # 前端资源缓存策略
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        root /var/www/amphoreus/frontend/dist;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 反向代理到 FastAPI（SSE 长连接需要特殊配置）
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 关键配置：禁用缓冲和代理缓存
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;

        # 允许跨域（如需独立域名部署时）
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # 静态资源目录（如图片）
    location /images/ {
        alias /var/www/amphoreus/images/;
        expires 30d;
    }
}
EOF

# 启用配置
sudo ln -sf /etc/nginx/sites-available/amphoreus /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 5.2 如有域名，配置 HTTPS（可选）

```bash
# 安装 certbot
sudo apt install -y certbot python3-certbot-nginx

# 申请 SSL 证书（替换为你的域名）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期已内置，无需额外配置
```

---

## 六、后端服务守护（Systemd）

### 6.1 创建服务文件

```bash
sudo tee /etc/systemd/system/amphoreus.service > /dev/null << 'EOF'
[Unit]
Description=Amphoreus Eternal Regression API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/amphoreus
Environment="PATH=/var/www/amphoreus/.venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/var/www/amphoreus/.env
ExecStart=/var/www/amphoreus/.venv/bin/uvicorn app.server:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=5

# 2核2G 资源保护
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable amphoreus
sudo systemctl start amphoreus
```

### 6.2 常用运维命令

```bash
# 查看状态
sudo systemctl status amphoreus

# 重启后端
sudo systemctl restart amphoreus

# 查看实时日志
sudo journalctl -u amphoreus -f

# 停止后端
sudo systemctl stop amphoreus
```

---

## 七、阿里云安全组配置

在阿里云控制台 → 云服务器 ECS → 安全组，确保入方向规则包含：

| 协议 | 端口 | 授权对象 | 说明 |
|------|------|----------|------|
| TCP | 80 | 0.0.0.0/0 | HTTP 访问 |
| TCP | 443 | 0.0.0.0/0 | HTTPS 访问（如已配置域名） |
| TCP | 22 | 你的本地IP/32 | SSH 管理（建议限制源 IP） |

> 注意：FastAPI 运行在 8000 端口，但只监听 `127.0.0.1`，**不暴露到公网**，由 Nginx 反向代理。安全组无需开放 8000。

---

## 八、部署验证

### 8.1 健康检查

```bash
# 测试前端
curl -I http://47.99.201.66/

# 测试后端 API（带密码参数）
curl "http://47.99.201.66/api/run_game?password=33550336@Neikos496&max_iterations=1&max_persuasions=1"
```

### 8.2 浏览器访问

- 前端：`http://47.99.201.66/`
- API 测试：`http://47.99.201.66/api/run_game?password=33550336@Neikos496&max_iterations=6&max_persuasions=3`

---

## 九、性能优化（2核2G 针对性）

### 9.1 减少内存占用

```bash
# 限制 Nginx worker 进程数
sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
user www-data;
worker_processes 1;          # 2核环境设为1-2即可
pid /run/nginx.pid;

events {
    worker_connections 768;
    use epoll;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript;
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

sudo nginx -t && sudo systemctl reload nginx
```

### 9.2 添加 Swap（防止内存不足）

```bash
# 创建 2GB Swap 文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 写入 fstab 确保持久化
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 验证
free -h
```

### 9.3 日志轮转（防止磁盘占满）

```bash
sudo tee /etc/logrotate.d/amphoreus > /dev/null << 'EOF'
/var/www/amphoreus/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
EOF
```

---

## 十、备份与升级

### 10.1 快速备份脚本

```bash
sudo tee /usr/local/bin/amphoreus-backup.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/amphoreus"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

tar czf $BACKUP_DIR/amphoreus_$DATE.tar.gz \
    -C /var/www amphoreus/.env \
    amphoreus/characters \
    amphoreus/main \
    amphoreus/app \
    amphoreus/frontend/dist

# 保留最近7份
ls -t $BACKUP_DIR/*.tar.gz | tail -n +8 | xargs -r rm
EOF

sudo chmod +x /usr/local/bin/amphoreus-backup.sh

# 加入每日定时任务（凌晨3点）
echo '0 3 * * * root /usr/local/bin/amphoreus-backup.sh' | sudo tee /etc/cron.d/amphoreus-backup
```

### 10.2 升级流程

```bash
cd /var/www/amphoreus

# 拉取最新代码
git pull

# 更新后端依赖
source .venv/bin/activate
pip install --no-cache-dir -r requirements.txt

# 重新构建前端
cd frontend
npm install
npm run build

# 重启服务
sudo systemctl restart amphoreus
sudo nginx -t && sudo systemctl reload nginx
```

---

## 十一、监控建议（可选轻量级方案）

2核2G 不建议跑完整的 Prometheus + Grafana，推荐阿里云原生监控：

1. **云监控**（免费）：阿里云控制台 → 云监控 → 主机监控，设置 CPU > 85% 或内存 > 90% 告警
2. **日志服务 SLS**：将 Nginx 日志 `/var/log/nginx/access.log` 接入，分析 API 调用频率
3. **Systemd 状态监控**：`sudo systemctl is-active amphoreus` 作为存活探针

---

## 十二、部署清单 Checklist

- [ ] 安全组已开放 80/443，22 已限制源 IP
- [ ] `.env` 文件已配置真实 API Key，权限 600
- [ ] 后端 `systemctl start amphoreus` 无报错
- [ ] Nginx `nginx -t` 配置测试通过
- [ ] 浏览器访问 `http://47.99.201.66/` 正常加载前端
- [ ] `curl /api/run_game` 返回 SSE 流数据
- [ ] Swap 已启用（`free -h` 验证）
- [ ] 日志轮转已配置
- [ ] 备份脚本已配置（如需要）

---

## 附录：一键部署脚本（可选）

如果你需要，可以将其保存为 `deploy.sh` 在服务器上直接运行：

```bash
#!/bin/bash
set -e

PROJECT_DIR="/var/www/amphoreus"

# 1. 环境安装
sudo apt update
sudo apt install -y nginx git python3-venv python3-pip

# 2. 后端部署
cd $PROJECT_DIR
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 前端构建
cd $PROJECT_DIR/frontend
npm install
npm run build

# 4. Nginx 配置
sudo cp $PROJECT_DIR/nginx/default.conf /etc/nginx/sites-available/amphoreus
sudo ln -sf /etc/nginx/sites-available/amphoreus /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# 5. 启动后端
sudo systemctl restart amphoreus

echo "✅ 部署完成，访问 http://47.99.201.66/"
```

---

**预估资源占用**：
- Nginx：~20MB 内存
- Python FastAPI：~150-300MB 内存（取决于并发和迭代轮数）
- 系统预留：~500MB
- 剩余可用：~1GB+（足够支撑模拟器运行）
