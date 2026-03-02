package com.openzhixue.communication.config;

import com.openzhixue.communication.websocket.WebSocketMessageHandler;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.SimpMessagingTemplate;

@Configuration
@RequiredArgsConstructor
public class WebSocketConfigHelper {

    private final SimpMessagingTemplate messagingTemplate;

    public SimpMessagingTemplate getMessagingTemplate() {
        return messagingTemplate;
    }
}
