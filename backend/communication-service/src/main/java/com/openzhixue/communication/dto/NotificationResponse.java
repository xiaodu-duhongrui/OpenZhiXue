package com.openzhixue.communication.dto;

import com.openzhixue.communication.entity.NotificationType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class NotificationResponse {
    private Long id;
    private Long userId;
    private String title;
    private String content;
    private NotificationType type;
    private Boolean isRead;
    private Long relatedId;
    private String relatedType;
    private LocalDateTime createdAt;
    private LocalDateTime readAt;
}
