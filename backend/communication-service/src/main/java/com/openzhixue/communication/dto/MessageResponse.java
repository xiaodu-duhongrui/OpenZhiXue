package com.openzhixue.communication.dto;

import com.openzhixue.communication.entity.MessageStatus;
import com.openzhixue.communication.entity.MessageType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MessageResponse {
    private Long id;
    private Long senderId;
    private Long receiverId;
    private String content;
    private MessageType type;
    private MessageStatus status;
    private Long conversationId;
    private String attachmentUrl;
    private String attachmentName;
    private Long attachmentSize;
    private LocalDateTime createdAt;
    private LocalDateTime readAt;
}
