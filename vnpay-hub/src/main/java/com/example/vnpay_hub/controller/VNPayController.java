package com.example.vnpay_hub.controller;


import com.example.event_library.VnpayTransaction;
import com.example.vnpay_hub.entity.Transaction;
import com.example.vnpay_hub.entity.TransactionStatus;
import com.example.vnpay_hub.repository.TransactionRepository;
import com.example.vnpay_hub.service.VNPayService;
import com.example.vnpay_hub.util.VNPayUtils;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/payment")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:6969") // Cấu hình origin để cho phép browser tải từ origin đó có thể gửi request
// Vì khi tải html sẽ mang theo origin để biết nguồn gốc render từ đâu
public class VNPayController {
    public final VNPayUtils utils;
    public final VNPayService service;
    public final TransactionRepository transactionRepository;

    @PostMapping("/order-request")
    public ResponseEntity<?> queryTransaction(
            @RequestBody VnpayTransaction vnPayDTO,
            HttpServletRequest request) { // Khai báo request ở đây

        String vnp_IpAddr = utils.getIpAddress(request);

        System.out.println("IP khách hàng: " + vnp_IpAddr);
        service.createParamURL(vnPayDTO, vnp_IpAddr);

        return ResponseEntity.ok().build();
    }

    @GetMapping("/vnpay-ipn")
    public ResponseEntity<?> processVNPayIPN(@RequestParam Map<String, String> requestParams) {
        Map<String, String> response = new HashMap<>();

        // 1. Lấy chữ ký bảo mật
        String hashCheck = requestParams.get("vnp_SecureHash");

        try {
            // 2. Nếu có tham số thật, tiến hành tính toán chữ ký thực tế từ Service
            String hashTrue = service.checkSum(requestParams);

            if (hashCheck.equals(hashTrue)) {
                System.out.println("====== XÁC THỰC CHỮ KÝ IPN THÀNH CÔNG ======");
                System.out.println("Dữ liệu nhận từ VNPAY: " + requestParams);

                String txnRef = requestParams.get("vnp_TxnRef");
                long vnpAmount = Long.parseLong(requestParams.get("vnp_Amount")) / 100;
                String responseCode = requestParams.get("vnp_ResponseCode");
                String transactionStatus = requestParams.get("vnp_TransactionStatus");

                Optional<Transaction> txOpt = transactionRepository.findByTxnRef(txnRef);

                // Case 1: Không tìm thấy order
                if (txOpt.isEmpty()) {
                    System.out.println("====== LỖI: KHÔNG TÌM THẤY ĐƠN HÀNG ======");
                    response.put("RspCode", "01");
                    response.put("Message", "Order not found");
                    return new ResponseEntity<>(response, HttpStatus.OK);
                }

                Transaction tx = txOpt.get();

                // Case 2: Amount không khớp -> nghi ngờ giả mạo
                if (!tx.getAmount().equals(vnpAmount)) {
                    System.out.println("====== LỖI: SAI SỐ TIỀN ======");
                    response.put("RspCode", "04");
                    response.put("Message", "Invalid amount");
                    return new ResponseEntity<>(response, HttpStatus.OK);
                }

                // Case 3: Order đã xử lý rồi -> chặn double processing (idempotency)
                if (tx.getStatus() != TransactionStatus.PENDING) {
                    System.out.println("====== ĐƠN HÀNG ĐÃ ĐƯỢC XỬ LÝ TRƯỚC ĐÓ ======");
                    response.put("RspCode", "02");
                    response.put("Message", "Order already confirmed");
                    return new ResponseEntity<>(response, HttpStatus.OK);
                }

                // Case 4: Hợp lệ -> update status theo kết quả thanh toán
                boolean isSuccess = "00".equals(responseCode) && "00".equals(transactionStatus);
                tx.setStatus(isSuccess ? TransactionStatus.SUCCESS : TransactionStatus.FAILED);
                transactionRepository.save(tx);

                System.out.println("====== CẬP NHẬT TRẠNG THÁI: " + tx.getStatus() + " ======");
                response.put("RspCode", "00");
                response.put("Message", "Confirm Success");
                return new ResponseEntity<>(response, HttpStatus.OK);
            } else {
                System.out.println("====== LỖI: CHỮ KÝ KHÔNG HỢP LỆ ======");
                response.put("RspCode", "97");
                response.put("Message", "Invalid Checksum");
                return new ResponseEntity<>(response, HttpStatus.OK);
            }
        } catch (Exception e) {
            System.out.println("====== LỖI HỆ THỐNG BACKEND ======");
            response.put("RspCode", "99");
            response.put("Message", "Unknown error");
            return new ResponseEntity<>(response, HttpStatus.OK);
        }
    }
}