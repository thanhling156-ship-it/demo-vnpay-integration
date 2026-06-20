package com.example.event_library;

import lombok.Data;

@Data
public class PayResult {
    private String userId;
    private String orderId;
    private String message;
    private String statusCode;
}
