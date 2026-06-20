package com.example.vnpay_hub.repository;

import com.example.vnpay_hub.entity.Transaction;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TransactionRepository extends JpaRepository<Transaction, String> {
    Optional<Transaction> findByTxnRef(String txnRef);
}
