package com.example.event_library;

import lombok.Data;

@Data
public class VnpayTransaction {
    private String userId; // Phục vụ cho websocket - không liên quan

    // 1. Các thông tin cấu hình hệ thống (mỗi đơn hàng đều cần có)
    private String vnp_Version = "2.1.0";
    private String vnp_Command = "pay";
    private String vnp_TmnCode; // #
    private String vnp_Locale = "vn";
    private String vnp_CurrCode = "VND";
    private String vnp_OrderType = "topup";
    private String vnp_ReturnUrl; // #

    // 2. Các thông tin động thay đổi theo từng đơn hàng cụ thể
    private String vnp_TxnRef;
    private String vnp_OrderInfo; // "Kiem tra ket qua GD OrderId:" + vnp_TxnRef
    private String vnp_IpAddr; // *

    // 3. Các thông tin dạng số học
    private String vnp_Amount; // *
    private String vnp_CreateDate;
    private String vnp_ExpireDate;

    // ở bên ngoài: "*"
    // ở trong utils: "#"
    // Những cái còn lại là cần tạo trong PayService
}
