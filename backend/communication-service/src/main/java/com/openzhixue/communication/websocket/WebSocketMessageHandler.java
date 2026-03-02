package com.openzhixue.communication.websocket;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.openzhixue.communication.dto.MessageResponse;
import com.openzhixue.communication.dto.NotificationResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Component
@RequiredArgsConstructor
public class WebSocketMessageHandler {

    private final SimpMessagingTemplate messagingTemplate;
    private final RedisTemplate<String, Object> redisTemplate;
    private final ObjectMapper objectMapper;

    private static final String ONLINE_USERS_KEY = "websocket:online:users";
    private static final String USER_SESSION_KEY = "websocket:user:session:";

    private final Map<Long, Set<String>> userSessions = new ConcurrentHashMap<>();

    public void sendMessageToUser(Long userId, MessageResponse message) {
        String destination = "/user/" + userId + "/queue/messages";
        messagingTemplate.convertAndSend(destination, message);
        log.debug("Message sent to user {}: {}", userId, message.getId());
    }

    public void sendNotificationToUser(Long userId, NotificationResponse notification) {
        String destination = "/user/" + userId + "/queue/notifications";
        messagingTemplate.convertAndSend(destination, notification);
        log.debug("Notification sent to user {}: {}", userId, notification.getId());
    }

    public void sendReadReceipt(Long userId, Long messageId) {
        Map<String, Object> receipt = new HashMap<>();
        receipt.put("messageId", messageId);
        receipt.put("readAt", System.currentTimeMillis());

        String destination = "/user/" + userId + "/queue/read-receipts";
        messagingTemplate.convertAndSend(destination, receipt);
        log.debug("Read receipt sent to user {} for message {}", userId, messageId);
    }

    public void sendOnlineStatus(Long userId, boolean online) {
        Map<String, Object> status = new HashMap<>();
        status.put("userId", userId);
        status.put("online", online);
        status.put("timestamp", System.currentTimeMillis());

        messagingTemplate.convertAndSend("/topic/online-status", status);
        log.debug("Online status broadcast for user {}: {}", userId, online);
    }

    public void userConnected(Long userId, String sessionId) {
        redisTemplate.opsForSet().add(ONLINE_USERS_KEY, userId.toString());
        redisTemplate.opsForValue().set(USER_SESSION_KEY + userId, sessionId);

        sendOnlineStatus(userId, true);
        log.info("User {} connected with session {}", userId, sessionId);
    }

    public void userDisconnected(Long userId, String sessionId) {
        redisTemplate.opsForSet().remove(ONLINE_USERS_KEY, userId.toString());
        redisTemplate.delete(USER_SESSION_KEY + userId);

        sendOnlineStatus(userId, false);
        log.info("User {} disconnected", userId);
    }

    public boolean isUserOnline(Long userId) {
        return Boolean.TRUE.equals(redisTemplate.opsForSet().isMember(ONLINE_USERS_KEY, userId.toString()));
    }

    public Set<Object> getOnlineUsers() {
        return redisTemplate.opsForSet().members(ONLINE_USERS_KEY);
    }

    public void broadcastToAll(String destination, Object message) {
        messagingTemplate.convertAndSend(destination, message);
        log.debug("Broadcast message to all users: {}", destination);
    }

    public void sendToUsers(Set<Long> userIds, String destination, Object message) {
        userIds.forEach(userId -> {
            messagingTemplate.convertAndSendToUser(userId.toString(), destination, message);
        });
    }

    public SimpMessagingTemplate messagingTemplate() {
        return messagingTemplate;
    }
}
