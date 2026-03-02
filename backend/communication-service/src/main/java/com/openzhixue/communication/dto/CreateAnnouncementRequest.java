package com.openzhixue.communication.dto;

import com.openzhixue.communication.entity.AnnouncementTargetType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

@Data
public class CreateAnnouncementRequest {
    @NotBlank(message = "公告标题不能为空")
    private String title;

    @NotBlank(message = "公告内容不能为空")
    private String content;

    @NotNull(message = "目标类型不能为空")
    private AnnouncementTargetType targetType;

    private List<Long> targetIds;

    private boolean publishImmediately = false;
}
