import asyncio
import websockets
import json
import webbrowser

# Coi như đã login thành công - websocket client tự kích hoạt và lắng nghe thông báo từ server
async def listen(user_id):
    uri = f"ws://localhost:7000/ws/orders/{user_id}"
    async with websockets.connect(uri) as ws:
        print(f"Connected, đang chờ thông báo cho user {user_id}...")
        while True:
            message = await ws.recv()
            try:
                linkQRcode = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"

                # 1. Parse chuỗi JSON thành Python Dictionary
                data = json.loads(message)

                stringQuery = data.get("message")
                full_link = f"{linkQRcode}?{stringQuery}"
                
                webbrowser.open(full_link)
                

            except json.JSONDecodeError as e:
                print(f"Chuỗi nhận được không phải là JSON hợp lệ: {e}")

user_id = input("Nhập userId: ")
asyncio.run(listen(user_id))
