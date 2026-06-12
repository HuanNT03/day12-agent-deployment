# Clothes Recommendation ReAct Agent (Day 12 Cloud Deployment Lab)

Kết hợp TẤT CẢ các khái niệm đưa ứng dụng AI lên môi trường production (production concepts) của Day 12 vào một dự án hoàn chỉnh: Clothing Advice Agent sử dụng ReAct Loop.

---

## 📁 Cấu Trúc Thư Mục (Repository Structure)

```text
your-repo/
├── app/
│   ├── main.py              # Main application (Entry point & ReAct Loop)
│   ├── config.py            # Configuration (12-Factor Env Loader)
│   ├── auth.py              # Authentication (API Key Protection)
│   ├── rate_limiter.py      # Rate limiting (Redis / In-memory sliding window)
│   └── cost_guard.py        # Cost protection (Daily USD budget guard)
├── utils/
│   └── mock_llm.py          # Mock LLM provider (Fallback)
├── screenshots/             # Thư mục lưu hình ảnh chạy thử & deployment
├── Dockerfile               # Multi-stage production Docker build
├── docker-compose.yml       # Full stack local composer (FastAPI + Redis)
├── requirements.txt         # Project dependencies
├── .env.example             # Template variables môi trường
├── .dockerignore            # Docker ignore file
├── railway.toml             # Railway configuration
├── render.yaml              # Render configuration
└── README.md                # Hướng dẫn setup và sử dụng này
```

---

## 🛠️ Checklist Deliverables đạt được

- [x] Dockerfile (multi-stage, < 500 MB, chạy non-root user)
- [x] docker-compose.yml (đầy đủ FastAPI agent + Redis cache service)
- [x] .dockerignore tránh bị rò rỉ thông tin cục bộ
- [x] Health check endpoint (`GET /health`) phục vụ liveness probe
- [x] Readiness endpoint (`GET /ready`) kiểm tra kết nối database/Redis
- [x] API Key authentication (xác thực qua header `X-API-Key`)
- [x] Rate limiting (giới hạn số request/phút theo từng API Key)
- [x] Cost guard (kiểm soát chi phí gọi LLM API theo budget ngày tự động)
- [x] Cấu hình 12-factor hoàn toàn từ environment variables
- [x] Structured JSON logging giúp theo dõi log dễ dàng
- [x] Graceful shutdown bắt tín hiệu SIGTERM dọn dẹp kết nối
- [x] Sẵn sàng deploy lên Railway / Render thông qua config file

---

## 🚀 Hướng Dẫn Chạy Local & Kiểm Thử

### 1. Setup Biến Môi Trường

Copy file cấu hình mẫu và điền các API key cần thiết:
```bash
cp .env.example .env
```
*Lưu ý: Nếu không cấu hình `DASHSCOPE_API_KEY`, agent sẽ tự động chạy ở chế độ giả lập (Mock ReAct Loop) với dữ liệu thời tiết Hà Nội và gợi ý quần áo cố định.*

### 2. Chạy với Docker Compose

Khởi động toàn bộ stack dịch vụ bao gồm FastAPI App và Redis Server:
```bash
docker compose -f docker-compose.yml up
```
*Mặc định, `docker-compose.yml` sẽ map cổng `80` của máy host vào cổng `8000` của container.*

### 3. Test Health Check
Kiểm tra liveness endpoint:
```bash
curl http://localhost/health
```

# Dừng toàn bộ
docker compose -f 02-docker/production/docker-compose.yml down

### 4. Lấy API Key từ `.env` và Test Endpoint `/ask`
Đọc tự động API key trong file `.env` của bạn để gửi request hỏi đáp về thời tiết và lựa chọn trang phục:
```bash
API_KEY=$(grep AGENT_API_KEY .env | cut -d= -f2)
curl -H "X-API-Key: $API_KEY" \
     -X POST http://localhost/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "Tôi muốn đi chơi Hà Nội hôm nay thì mặc gì?"}'
```

---

## ☁️ Deploy Lên Cloud

### Triển khai lên Railway (< 5 phút)

Sử dụng CLI của Railway để khởi chạy dự án cực nhanh:
```bash
# Cài Railway CLI toàn cục
npm i -g @railway/cli

# Login tài khoản và khởi tạo project
railway login
railway init

# Thiết lập các biến môi trường bí mật cần thiết
railway variables set DASHSCOPE_API_KEY=your-api-key-here
railway variables set BASE_URL=your-secret-url

# Tiến hành deploy
railway up

# Nhận tên miền công khai công bố dịch vụ!
railway domain
```

### Triển khai lên Render

1. Đẩy mã nguồn này lên một kho lưu trữ GitHub mới của bạn.
2. Truy cập vào Dashboard của Render → chọn **New** → **Blueprint**.
3. Kết nối với repo GitHub của bạn, Render sẽ tự động phát hiện và đọc cấu hình từ file [render.yaml](file:///home/huan/Develop/Github/Day12-Lab/Day12-agent-deployment/render.yaml).
4. Thiết lập các biến môi trường tương ứng: `DASHSCOPE_API_KEY` và `AGENT_API_KEY`.
5. Tiến hành Deploy. Khi quá trình build Docker hoàn tất, bạn sẽ nhận được một Public URL từ Render.

---

## 🔍 Kiểm Tra Production Readiness

Trước khi đẩy code lên staging/production, chạy script kiểm thử tự động để đảm bảo ứng dụng tuân thủ hoàn toàn tiêu chuẩn bảo mật và vận hành:
```bash
# Kích hoạt môi trường ảo
source .venv/bin/activate

# Chạy script checklist kiểm thử
python check_production_ready.py
```
Script này giúp bạn phát hiện sớm các lỗi cấu hình thiếu sót, đảm bảo tỷ lệ hoàn thành checklist đạt 100% chuẩn sản xuất!
