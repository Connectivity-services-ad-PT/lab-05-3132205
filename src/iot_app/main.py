import os
import uuid
import logging
import requests
from fastapi import FastAPI, Security, BackgroundTasks, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Cấu hình log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AI-Vision")

app = FastAPI(title="Smart Campus — AI Vision Service", version="1.0.0")
security_agent = HTTPBearer()

# Lấy Token từ biến môi trường
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "smart-campus-secret-token")
NHOM6_URL = "http://26.137.61.149:8000/api/v1/receive"

class ImageRequest(BaseModel):
    image_url: str
    timestamp: Optional[str] = None

# Hàm kiểm tra sức khỏe hệ thống
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-vision-service", "version": "1.0.0"}

def send_to_nhom6(data: dict):
    try:
        response = requests.post(NHOM6_URL, json=data, timeout=5)
        if response.status_code in [200, 201]:
            logger.info(f"ĐÃ GỬI THÀNH CÔNG sang Nhóm 6. ID: {data['detection_id']}")
        else:
            logger.warning(f"Nhóm 6 phản hồi lỗi: {response.status_code}")
    except Exception as e:
        logger.error(f"Lỗi kết nối Nhóm 6: {str(e)}")

@app.post("/api/v1/vision/detect", status_code=201)
def analyze_image(
    payload: ImageRequest, 
    background_tasks: BackgroundTasks, 
    credentials: HTTPAuthorizationCredentials = Security(security_agent)
):
    # 1. Kiểm tra Token
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. Log thông tin nhận được
    logger.info(f"--- ĐÃ NHẬN LINK TỪ NHÓM 2: {payload.image_url} ---")

    # 3. Phân tích (Giả lập)
    analysis_result = {
        "detection_id": f"DET-{uuid.uuid4().hex[:8].upper()}",
        "label": "person", 
        "confidence": 0.96,
        "created_at": datetime.now().isoformat()
    }
    
    logger.info(f"Phân tích hoàn tất: {analysis_result['label']} - ID: {analysis_result['detection_id']}")

    # 4. Gửi sang Nhóm 6 qua nền
    background_tasks.add_task(send_to_nhom6, analysis_result)

    return analysis_result