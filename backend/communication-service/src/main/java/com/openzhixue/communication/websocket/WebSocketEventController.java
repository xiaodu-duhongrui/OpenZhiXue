package com.openzhixue.communication.websocket;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.simp.SimpMessageHeaderAccessor;
import org.springframework.messaging.simp.annotation.SendToUser;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;

import java.util.Map;

@Slf4j
@Controller
@RequiredArgsConstructor
public class WebSocketEventController {

    private final WebSocketMessageHandler webSocketMessageHandler;

    @MessageMapping("/typing")
    public void handleTyping(@Payload Map<String, Object> payload, SimpMessageHeaderAccessor headerAccessor) {
        Authentication auth = (Authentication) headerAccessor.getUser();
        if (auth != null) {
            Long userId = (Long) auth.getPrincipal();
            Long receiverId = Long.valueOf(payload.get("receiverId").toString());
            boolean isTyping = Boolean.parseBoolean(payload.get("isTyping").toString());

            Map<String, Object> typingStatus = Map.of(
                    "userId", userId,
                    "isTyping", isTyping,
                    "timestamp", System.currentTimeMillis()
            );

            webSocketMessageHandler.messagingTemplate()
                    .convertAndSendToUser(receiverId.toString(), "/queue/typing", typingStatus);
        }
    }

    @MessageMapping("/online-users")
    @SendToUser("/queue/online-users")
    public Object getOnlineUsers() {
        return webSocketMessageHandler.getOnlineUsers();
    }

    @MessageMapping("/heartbeat")
    public void handleHeartbeat(SimpMessageHeaderAccessor headerAccessor) {
        Authentication auth = (Authentication) headerAccessor.getUser();
        if (auth != null) {
            Long userId = (Long) auth.getPrincipal();
            log.debug("Heartbeat received from user {}", userId);
        }
    }
}
