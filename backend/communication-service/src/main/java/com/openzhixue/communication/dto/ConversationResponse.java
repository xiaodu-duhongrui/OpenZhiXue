package com.openzhixue.communication.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConversationResponse {
    private Long id;
    private List<Long> participants;
    private String lastMessage;
    private String lastMessageType;
    private Long lastMessageSenderId;
    private Integer unreadCount;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    private Long otherUserId;
    private String otherUserName;
    private String otherUserAvatar;
}
