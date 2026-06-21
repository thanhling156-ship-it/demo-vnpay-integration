from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# =====================================================================
# ENDPOINT 1: TRANG CHỦ CHÍNH (MAIN BOARD) - ĐỊA CHỈ: http://localhost:6969/
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Hệ thống Điều Khiển Trung Tâm</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8f9fa; margin: 40px; }
            .container { max-width: 500px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin: 0 auto; }
            h2 { color: #212529; margin-top: 0; margin-bottom: 20px; font-size: 22px; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; color: #495057; }
            input { width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; font-size: 16px; }
            button { color: white; padding: 12px 15px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold; transition: background 0.2s; }
            .btn-primary { background: #0d6efd; width: 100%; }
            .btn-primary:hover { background: #0b5ed7; }
            .btn-danger { background: #dc3545; padding: 8px 12px; font-size: 14px; margin-top: 15px; width: 100%; }
            .btn-danger:hover { background: #bb2d3b; }
            #status-box { margin-top: 20px; padding: 12px; background: #e9ecef; border-radius: 4px; font-size: 14px; color: #495057; line-height: 1.5; }
            .hidden { display: none; }
            ul { padding-left: 20px; margin-top: 5px; }
            li { margin-bottom: 5px; background: #fff; padding: 6px; border-radius: 4px; border-left: 3px solid #0d6efd; list-style-type: none;}
        </style>
    </head>
    <body>
        <div class="container">
            <div id="loginScreen">
                <h2>Đăng Nhập Hệ Thống</h2>
                <div class="form-group">
                    <label>Nhập User ID để bắt đầu:</label>
                    <input type="text" id="userIdInput" value="user-001">
                </div>
                <button class="btn-primary" onclick="handleLogin()">Xác nhận & Khởi tạo</button>
            </div>

            <div id="mainBoardScreen" class="hidden">
                <h2>Bàn Điều Khiển Trung Tâm (<span id="displayUserId"></span>)</h2>
                
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button class="btn-primary" onclick="openNewActionTab()">Mở Tab Tạo Đơn Hàng (Postman)</button>
                    <button class="btn-danger" onclick="handleLogout()">Đăng xuất (Hủy phiên)</button>
                </div>

                <div id="status-box">Đang kết nối hệ thống ngầm...</div>
            </div>
        </div>

        <script>
            let ws = null;

            function handleLogin() {
                const userId = document.getElementById("userIdInput").value.trim();
                if (!userId) return alert("Vui lòng nhập User ID");

                localStorage.setItem("GLOBAL_APP_USER_ID", userId);
                localStorage.setItem("MAIN_BOARD_OPENED", "true");
                sessionStorage.setItem("IS_MAIN_BOARD", "true");

                initMainBoard();
            }

            function initMainBoard() {
                const globalUserId = localStorage.getItem("GLOBAL_APP_USER_ID");
                if (!globalUserId) {
                    showScreen("login");
                    return;
                }

                showScreen("main");
                document.getElementById("displayUserId").innerText = globalUserId;
                window.addEventListener('beforeunload', handleBeforeUnload);
                
                if (!ws) { connectWebSocket(globalUserId); }
                renderNotificationKhay();
            }

            function connectWebSocket(userId) {
                ws = new WebSocket(`ws://localhost:7000/ws/orders/${userId}`);

                ws.onopen = () => {
                    document.getElementById("status-box").innerHTML = `<strong>Trạng thái:</strong> Đã kết nối WebSocket cổng 7000. Đang lắng nghe kết quả xử lý từ hệ thống...`;
                };

                ws.onclose = () => {
                    document.getElementById("status-box").innerHTML = `<strong>Trạng thái:</strong> Mất kết nối tới cổng 7000.`;
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        const stringQuery = data.message;

                        const orderId = data.orderId || "Không rõ ID";
                        
                        if (stringQuery) {
                            // Main board ghi nhận vào khay thông báo lịch sử chung khi có cập nhật
                            const list = JSON.parse(localStorage.getItem("payment_notifications_list") || "[]");
                            const notificationContent = `${stringQuery} (Order ID: ${orderId})`;
                            list.push({ id: Date.now(), query: notificationContent, time: new Date().toLocaleTimeString() });
                            localStorage.setItem("payment_notifications_list", JSON.stringify(list));
                        }
                    } catch (e) { console.error(e); }
                };
            }

            function openNewActionTab() {
                window.open("/action", "_blank");
            }

            window.addEventListener('storage', (event) => {
                if (event.key === "payment_notifications_list") { renderNotificationKhay(); }
            });

            function renderNotificationKhay() {
                const list = JSON.parse(localStorage.getItem("payment_notifications_list") || "[]");
                const box = document.getElementById("status-box");
                if (list.length === 0) return;

                let html = "<strong>Khay thông báo chung:</strong><ul>";
                list.forEach(item => { html += `<li>[${item.time}] Đồng bộ dữ liệu thành công.</li>`; });
                html += "</ul>";
                box.innerHTML = html;
            }

            function handleLogout() {
                window.removeEventListener('beforeunload', handleBeforeUnload);
                localStorage.clear();
                if (ws) ws.close();
                location.reload();
            }

            function handleBeforeUnload(e) {
                // 1. Dọn dẹp sạch dữ liệu phiên làm việc trong localStorage
                localStorage.removeItem("MAIN_BOARD_OPENED");
                localStorage.removeItem("GLOBAL_APP_USER_ID");
                localStorage.removeItem("payment_notifications_list"); // Xóa luôn khay thông báo nếu muốn sạch hoàn toàn

                // 2. Kích hoạt hộp thoại cảnh báo của trình duyệt
                e.preventDefault();
                e.returnValue = "Bạn có chắc chắn muốn thoát? Các tab phụ sẽ mất kết nối.";
            }

            function showScreen(screen) {
                if (screen === "login") {
                    document.getElementById("loginScreen").classList.remove("hidden");
                    document.getElementById("mainBoardScreen").classList.add("hidden");
                } else {
                    document.getElementById("loginScreen").classList.add("hidden");
                    document.getElementById("mainBoardScreen").classList.remove("hidden");
                }
            }

            window.onload = initMainBoard;
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# =====================================================================
# ENDPOINT 2: TRANG PHỤ CHỨC NĂNG (POSTMAN FAKE) - ĐỊA CHỈ: http://localhost:6969/action
# =====================================================================
@app.get("/action", response_class=HTMLResponse)
async def get_action_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Công cụ Tạo Đơn Hàng (Postman)</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; margin: 40px; }
            .container { max-width: 450px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin: 0 auto; }
            h2 { color: #212529; margin-top: 0; margin-bottom: 20px; font-size: 22px; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; color: #495057; }
            input { width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #ced4da; border-radius: 4px; font-size: 16px; background: #e9ecef; }
            input[active] { background: white; }
            button { background: #198754; color: white; padding: 12px 15px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold; transition: background 0.2s; }
            button:hover { background: #157347; }
            #status-box { margin-top: 20px; padding: 12px; background: #e9ecef; border-radius: 4px; font-size: 14px; color: #495057; line-height: 1.5; }
            ul { padding-left: 20px; margin-top: 5px; }
            li { margin-bottom: 5px; background: #fff; padding: 6px; border-radius: 4px; border-left: 3px solid #198754; list-style-type: none;}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Nhập hàng & Tạo đơn</h2>
            
            <div class="form-group">
                <label>User ID (Cố định từ hệ thống):</label>
                <input type="text" id="displayUserId" readonly>
            </div>
            
            <div class="form-group">
                <label>Số tiền (vnp_Amount):</label>
                <input type="text" id="vnp_Amount" value="10000000" active required>
            </div>
            
            <button onclick="submitOrder()">Bấm Tạo Đơn Hàng</button>

            <div id="status-box">Đang đồng bộ dữ liệu...</div>
        </div>

        <script>
            function initActionTab() {
                const globalUserId = localStorage.getItem("GLOBAL_APP_USER_ID");
                const isMainBoardAlive = localStorage.getItem("MAIN_BOARD_OPENED");

                if (!globalUserId || isMainBoardAlive !== "true") {
                    alert("Phiên làm việc không hợp lệ hoặc đã đăng xuất. Đang quay lại trang login.");
                    window.location.href = "/";
                    return;
                }

                document.getElementById("displayUserId").value = globalUserId;
                document.getElementById("status-box").innerHTML = "Hệ thống sẵn sàng. Nhập số tiền và bấm tạo đơn.";
                renderNotificationKhay();
            }

            // SỬA TẠI ĐÂY: NHẬN TRỰC TIẾP URL TỪ RESPONSE VÀ MỞ MỚI LUÔN
            async function submitOrder() {
                const globalUserId = localStorage.getItem("GLOBAL_APP_USER_ID");
                const amount = document.getElementById("vnp_Amount").value;
                
                document.getElementById("status-box").innerText = "Đang gửi yêu cầu tạo đơn sang cổng 7002...";

                try {
                    const response = await fetch("http://localhost:7002/api/payment/order-request", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ userId: globalUserId, vnp_Amount: amount })
                    });

                    if (response.ok) {
                        const resData = await response.json();
                        // Bốc chính xác thuộc tính paymentUrl từ JSON trả về của Spring Boot
                        const query = resData.query; 

                        if (query) {
                            document.getElementById("status-box").innerText = "Tạo link thành công! Đang chuyển hướng sang VNPAY...";
                            
                            // Mở trực tiếp link thanh toán VNPAY trên một tab mới luôn
                            window.open(`https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?${query}`, '_blank');
                            
                            // Ghi nhận sự kiện này vào khay thông báo chung để Main Board đồng bộ lịch sử
                            const list = JSON.parse(localStorage.getItem("payment_notifications_list") || "[]");
                            list.push({ id: Date.now(), query: "Đã khởi tạo đơn hàng từ cổng 7002", time: new Date().toLocaleTimeString() });
                            localStorage.setItem("payment_notifications_list", JSON.stringify(list));
                        } else {
                            document.getElementById("status-box").innerText = "Không tìm thấy dữ liệu paymentUrl từ Server.";
                        }
                    } else {
                        document.getElementById("status-box").innerText = `Cổng 7002 báo lỗi status: ${response.status}`;
                    }
                } catch (error) {
                    document.getElementById("status-box").innerText = `Lỗi kết nối tới cổng 7002: ${error}`;
                }
            }

            window.addEventListener('storage', (event) => {
                if (event.key === "payment_notifications_list") {
                    renderNotificationKhay();
                }
                if (event.key === "GLOBAL_APP_USER_ID" && !event.newValue) {
                    location.reload();
                }
            });

            function renderNotificationKhay() {
                const list = JSON.parse(localStorage.getItem("payment_notifications_list") || "[]");
                const box = document.getElementById("status-box");
                if (list.length === 0) return;

                let html = "<strong>Khay thông báo chung:</strong><ul>";
                list.forEach(item => {
                    html += `<li>[${item.time}] ${item.query}</li>`;
                });
                html += "</ul>";
                box.innerHTML = html;
            }

            window.onload = initActionTab;
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=6969, reload=True)