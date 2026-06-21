package com.example.vnpay_hub.service;

import com.example.event_library.PayResult;
import com.example.event_library.VnpayTransaction;
import com.example.vnpay_hub.entity.Transaction;
import com.example.vnpay_hub.entity.TransactionStatus;
import com.example.vnpay_hub.repository.TransactionRepository;
import com.example.vnpay_hub.util.VNPayUtils;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.io.UnsupportedEncodingException;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class VNPayService {
    private final VNPayUtils utils;
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final TransactionRepository transactionRepository;
    public String createParamURL (VnpayTransaction transaction, String ipAddr){

        String vnp_Txnref =  utils.getRandomNumber(8);
        ZonedDateTime gmt7Time = ZonedDateTime.now(ZoneId.of("Asia/Ho_Chi_Minh"));
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");
        String vnp_CreateDate = gmt7Time.format(formatter);
        String vnp_ExpireDate = gmt7Time.plusHours(1).format(formatter);
        String vnp_OrderInfo = "Kiem tra ket qua GD OrderId:" + vnp_Txnref;

        transaction.setVnp_IpAddr(ipAddr);
        transaction.setVnp_TxnRef(vnp_Txnref);
        transaction.setVnp_CreateDate(vnp_CreateDate);
        transaction.setVnp_ExpireDate(vnp_ExpireDate);
        transaction.setVnp_OrderInfo(vnp_OrderInfo);
        transaction.setVnp_TmnCode(utils.getVnp_TmnCode());
        transaction.setVnp_ReturnUrl(utils.getVnp_ReturnUrl());
        ObjectMapper objectMapper = new ObjectMapper();
        Map<String, String> vnpayMap = objectMapper.convertValue(transaction, Map.class);

        String amountStr = transaction.getVnp_Amount(); // "10000000"
        Long amount = Long.parseLong(amountStr) / 100; // 100000 VND

        Transaction tx = Transaction.builder()
                .txnRef(vnp_Txnref)
                .amount(amount)
                .status(TransactionStatus.PENDING)
                .createdAt(LocalDateTime.now())
                .userId(transaction.getUserId())
                .build();

        transactionRepository.save(tx);

        vnpayMap.remove("userId");
        vnpayMap.remove("requestId"); // Loại bỏ kẻ phá bĩnh chữ ký
        vnpayMap.remove("vnp_SecureHash"); // Đảm bảo hash không tự băm chính


        String paymentUrl = "";
        try {
            paymentUrl = utils.generateSecureHash(vnpayMap);
            log.info("Payment URL: " + paymentUrl);
        } catch (IllegalArgumentException e) {
            // Xử lý khi thiếu tham số đầu vào
            String errorMsg = String.format("Lỗi khởi tạo thanh toán: %s", e.getMessage());
            log.error(errorMsg);
        } catch (UnsupportedEncodingException e) {
            // Xử lý lỗi hệ thống liên quan đến bảng mã mã hóa
            String errorMsg = String.format("Hệ thống không hỗ trợ bảng mã UTF-8 %s", e);
            log.error(errorMsg);
            throw new RuntimeException("Lỗi cấu hình hệ thống.", e);
        }
        finally {
            return paymentUrl;
        }
    }

    public void sendStatus(PayResult result, String topic) {
        kafkaTemplate.send(topic, result);
    }

    public String checkSum(Map<String, String> requestParams) {
        String vnp_SecureHash = requestParams.get("vnp_SecureHash");
        requestParams.remove("vnp_SecureHash");
        requestParams.remove("vnp_SecureHashType");

        try {
            String trueQueryString = utils.generateSecureHash(requestParams);
            String[] parts = trueQueryString.split("&vnp_SecureHash=");

            if (parts.length > 1) {
                String secureHashValue = parts[1]; // Lấy phần tử phía sau
                return secureHashValue;
            }
        }
        catch (UnsupportedEncodingException e){
            throw new RuntimeException("Lỗi cấu hình hệ thống.", e);
        }
        return null;
    }
}
