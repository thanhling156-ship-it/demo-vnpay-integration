from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# ĐÂY LÀ ENDPOINT DUY NHẤT CỦA FILE NÀY
@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Công cụ nhập hàng thay thế Postman</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8f9fa; margin: 40px; }
            .container { max-width: 450px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin: 0 auto; }
            h2 { color: #212529; margin-top: 0; margin-bottom: 20px; font-size: 22px; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; color: #495057; }
            input { width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; font-size: 16px; }
            button { background: #0d6efd; color: white; padding: 12px 15px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold; width: 100%; transition: background 0.2s; }
            button:hover { background: #0b5ed7; }
            #status { margin-top: 20px; padding: 12px; background: #e9ecef; border-radius: 4px; font-size: 14px; color: #495057; line-height: 1.5; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Nhập hàng & Thanh toán</h2>
            
            <form id="orderForm" onsubmit="submitOrder(event)">
                <div class="form-group">
                    <label>User ID:</label>
                    <input type="text" id="userId" value="user-001" onchange="connectToRealWebSocket()" required>
                </div>
                
                <div class="form-group">
                    <label>Số tiền (vnp_Amount):</label>
                    <input type="text" id="vnp_Amount" value="10000000" required>
                </div>
                
                <button type="submit">Xác nhận đơn hàng</button>
            </form>

            <div id="status">Đang khởi tạo kết nối...</div>
        </div>

        <script>
            let ws;

            // 1. Browser tự động cắm Socket trực tiếp sang Server thật cổng 7000 của bạn
            function connectToRealWebSocket() {
                const userId = document.getElementById("userId").value;
                if (!userId) return;

                if (ws) { ws.close(); }

                ws = new WebSocket(`ws://localhost:7000/ws/orders/${userId}`);

                ws.onopen = () => {
                    document.getElementById("status").innerHTML = `<strong>Trạng thái:</strong> Đã kết nối WebSocket tới <code>localhost:7000</code> (ID: ${userId})`;
                };

                ws.onclose = () => {
                    document.getElementById("status").innerHTML = "<strong>Trạng thái:</strong> Mất kết nối tới localhost:7000";
                };

                // 2. Nhận cục stringQuery chứa SecureHash từ cổng 7000 qua WebSocket và tự mở tab VNPAY
                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        const stringQuery = data.message;
                        
                        if (stringQuery) {
                            const linkQRcode = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html";
                            const full_link = `${linkQRcode}?${stringQuery}`;

                            // Cơ chế chặn mở trùng lặp tab bằng LocalStorage khi mở nhiều tab
                            const lockKey = "vnpay_opening_lock";
                            const now = Date.now();
                            const lastOpen = localStorage.getItem(lockKey);

                            if (!lastOpen || (now - parseInt(lastOpen) > 2000)) {
                                localStorage.setItem(lockKey, now.toString());
                                window.open(full_link);
                            }
                        }
                    } catch (e) {
                        console.error("Lỗi dữ liệu:", e);
                    }
                };
            }

            // 3. Khi bấm nút, Browser bắn dữ liệu TRỰC TIẾP sang Server xử lý riêng cổng 7002 của bạn
            async function submitOrder(event) {
                event.preventDefault();
                const userId = document.getElementById("userId").value;
                const vnp_Amount = document.getElementById("vnp_Amount").value;

                document.getElementById("status").innerText = "Đang gửi yêu cầu tạo đơn hàng...";

                try {
                    const response = await fetch("http://localhost:7002/api/payment/order-request", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ userId: userId, vnp_Amount: vnp_Amount })
                    });

                    // Thay vì dùng response.json(), chỉ cần kiểm tra response.ok (mã 200-299)
                    if (response.ok) {
                        document.getElementById("status").innerHTML = `<strong>Trạng thái:</strong> Đã gửi đơn sang cổng 7002 thành công.`;
                    } else {
                        document.getElementById("status").innerText = `Server 7002 trả về lỗi: ${response.status}`;
                    }
                } catch (error) {
                    document.getElementById("status").innerText = `Lỗi kết nối tới cổng 7002: ${error}`;
                }
            }

            // Chạy kết nối tự động khi vừa tải trang
            connectToRealWebSocket();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    # File này chạy trên một port bất kỳ, ví dụ 8080 để phát giao diện cho Browser mang về
    uvicorn.run("app:app", host="127.0.0.1", port=6969, reload=True)