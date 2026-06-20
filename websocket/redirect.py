from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
base_url = "http://localhost:6969/"

@app.get("/api/v1/vnpay-callback", response_class=HTMLResponse)
async def vnpay_callback(request: Request):
    params = dict(request.query_params)
    
    # Đọc thông tin từ VNPAY gửi về
    vnp_response_code = params.get("vnp_ResponseCode")
    vnp_txn_ref = params.get("vnp_TxnRef")
    vnp_amount = params.get("vnp_Amount")
    
    amount_formatted = "{:,.0f}".format(float(vnp_amount) / 100) if vnp_amount else "0"

    # Khởi tạo biến giao diện tùy thuộc vào trạng thái
    if vnp_response_code == "00":
        status_class = "success"
        status_icon = "✓"
        status_title = "Thanh Toán Thành Công!"
        status_message = f"Cảm ơn bạn. Đơn hàng <strong>#{vnp_txn_ref}</strong> đã được thanh toán hoàn tất."
    else:
        status_class = "error"
        status_icon = "✕"
        status_title = "Thanh Toán Thất Bại"
        status_message = f"Giao dịch cho đơn hàng <strong>#{vnp_txn_ref}</strong> không thành công hoặc đã bị hủy (Mã lỗi: {vnp_response_code})."

    # Chuỗi HTML Frontend giao diện kết quả thanh toán
    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kết quả thanh toán VNPAY</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f6f9;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                text-align: center;
                max-width: 450px;
                width: 100%;
            }}
            .icon {{
                width: 70px;
                height: 70px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 32px;
                font-weight: bold;
                margin: 0 auto 20px;
            }}
            .success .icon {{
                background-color: #e6f7ed;
                color: #2ecc71;
            }}
            .error .icon {{
                background-color: #fde8e8;
                color: #e74c3c;
            }}
            h2 {{
                margin-bottom: 10px;
                color: #2c3e50;
            }}
            p {{
                color: #7f8c8d;
                font-size: 15px;
                line-height: 1.6;
            }}
            .amount {{
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 6px;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #0056b3;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                margin-top: 15px;
                transition: background 0.2s;
            }}
            .btn:hover {{
                background-color: #004085;
            }}
        </style>
    </head>
    <body>
        <div class="card {status_class}">
            <div class="icon">{status_icon}</div>
            <h2>{status_title}</h2>
            <p>{status_message}</p>
            {"<div class='amount'>" + amount_formatted + " VND</div>" if vnp_response_code == "00" else ""}
            <a href="{base_url}" class="btn">Quay lại trang chủ</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run("redirect:app", host="127.0.0.1", port=8080, reload=True)