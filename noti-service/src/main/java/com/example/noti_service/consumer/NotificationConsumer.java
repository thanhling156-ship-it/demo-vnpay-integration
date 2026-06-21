package com.example.noti_service.consumer;

import com.example.event_library.PayResult;
import com.example.noti_service.handler.NotificationHandler;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import tools.jackson.databind.ObjectMapper;

import java.util.Map;

@Component
@Slf4j
@RequiredArgsConstructor
public class NotificationConsumer {
    private final NotificationHandler notificationHandler;
    private final ObjectMapper objectMapper;
    @KafkaListener(topics = "payment-notification", groupId = "noti-group")
    public void handleCreatingTransactionSuccess(PayResult event) {
        String userId = event.getUserId();
        Map<String, String> eventMap = objectMapper.convertValue(event, Map.class);
        eventMap.remove("userId");
        String messageJson = objectMapper.writeValueAsString(eventMap);
        notificationHandler.pushNotification(userId, messageJson);
    }
}
