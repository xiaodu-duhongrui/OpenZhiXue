package com.openzhixue.communication.dto;

import com.openzhixue.communication.entity.MessageType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class SendMessageRequest {
    @NotNull(message = "接收者ID不能为空")
    private Long receiverId;

    @NotBlank(message = "消息内容不能为空")
    private String content;

    private MessageType type = MessageType.TEXT;

    private String attachmentUrl;

    private String attachmentName;

    private Long attachmentSize;
}
