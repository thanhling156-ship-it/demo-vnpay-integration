package com.example.vnpay_hub.entity;

import jakarta.persistence.Column;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;

public enum TransactionStatus {
    PENDING, SUCCESS, FAILED
}
