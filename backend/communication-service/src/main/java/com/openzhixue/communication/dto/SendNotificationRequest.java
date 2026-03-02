package com.openzhixue.communication.dto;

import com.openzhixue.communication.entity.NotificationType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class SendNotificationRequest {
    @NotNull(message = "用户ID不能为空")
    private Long userId;

    @NotBlank(message = "通知标题不能为空")
    private String title;

    @NotBlank(message = "通知内容不能为空")
    private String content;

    @NotNull(message = "通知类型不能为空")
    private NotificationType type;

    private Long relatedId;

    private String relatedType;
}
