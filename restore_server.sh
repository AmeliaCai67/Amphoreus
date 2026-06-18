#!/bin/bash
# 恢复 Amphoreus 部署 - 以 root 运行
# 仓库路径: /home/amelia/projects/Amphoreus

set -e

echo "=== 0. 修复 git 安全目录警告 ==="
git config --global --add safe.directory /home/amelia/projects/Amphoreus

cd /home/amelia/projects/Amphoreus

echo ""
echo "=== 1. 检查 .env 内容（注意：只有 53 字节，可能不完整）==="
cat .env
echo "---"

echo ""
echo "=== 2. 检查最新 git 状态 ==="
git log --oneline -1
git branch --show-current

echo ""
echo "=== 3. 创建 Python 虚拟环境并安装依赖 ==="
python3 -m venv .venv
source .venv/bin/activate
pip install --no-cache-dir -r requirements.txt

echo ""
echo "=== 4. 确认前端 dist 已存在 ==="
ls -la frontend/dist/index.html 2>/dev/null && echo "✅ 前端已构建" || echo "❌ 需要重新构建前端"

echo ""
echo "=== 5. 创建 Nginx 配置（路径指向 /home/amelia/projects/Amphoreus）==="
cat > /etc/nginx/sites-available/amphoreus << 'NGINX_EOF'
server {
    listen 80;
    server_name 47.99.201.66;

    # 前端静态文件
    location / {
        root /home/amelia/projects/Amphoreus/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        root /home/amelia/projects/Amphoreus/frontend/dist;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 反向代理到 FastAPI（SSE 长连接）
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # 角色图片
    location /images/ {
        alias /home/amelia/projects/Amphoreus/images/;
        expires 30d;
    }
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/amphoreus /etc/nginx/sites-enabled/default
nginx -t

echo ""
echo "=== 6. 创建 Systemd 服务文件（注意用户为 root 但路径指向 amelia 的项目）==="
cat > /etc/systemd/system/amphoreus.service << 'SYSTEMD_EOF'
[Unit]
Description=Amphoreus Eternal Regression API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/amelia/projects/Amphoreus
Environment="PATH=/home/amelia/projects/Amphoreus/.venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/home/amelia/projects/Amphoreus/.env
ExecStart=/home/amelia/projects/Amphoreus/.venv/bin/uvicorn app.server:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

systemctl daemon-reload

echo ""
echo "=== 7. 启动所有服务 ==="
systemctl enable nginx
systemctl restart nginx
systemctl enable amphoreus
systemctl start amphoreus

echo ""
echo "=== 8. 验证状态 ==="
echo "--- Nginx 状态 ---"
systemctl status nginx --no-pager

echo ""
echo "--- Amphoreus 后端状态 ---"
systemctl status amphoreus --no-pager

echo ""
echo "--- 监听端口 ---"
netstat -tlnp 2>/dev/null | grep -E "8000|80" || ss -tlnp | grep -E "8000|80"

echo ""
echo "✅ 部署恢复完成！"
echo "前端: http://47.99.201.66/"
echo "API:  http://47.99.201.66/api/run_game?password=33550336@Neikos496&max_iterations=1"
echo ""
echo "日志查看: journalctl -u amphoreus -f"
