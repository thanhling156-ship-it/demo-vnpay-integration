package com.example.noti_service.consumer;

import com.example.event_library.PayResult;
import com.example.noti_service.handler.NotificationHandler;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import tools.jackson.databind.ObjectMapper;

@Component
@Slf4j
@RequiredArgsConstructor
public class NotificationConsumer {
    private final NotificationHandler notificationHandler;
    private final ObjectMapper objectMapper;
    @KafkaListener(topics = "create-transaction-success", groupId = "noti-group")
    public void handleCreatingTransactionSuccess(PayResult event) {
        String userId = event.getUserId();
        String messageJson = objectMapper.writeValueAsString(event);
        notificationHandler.pushNotification(userId, messageJson);
    }
}
