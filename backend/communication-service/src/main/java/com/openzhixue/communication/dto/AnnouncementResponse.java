package com.openzhixue.communication.dto;

import com.openzhixue.communication.entity.AnnouncementStatus;
import com.openzhixue.communication.entity.AnnouncementTargetType;
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
public class AnnouncementResponse {
    private Long id;
    private String title;
    private String content;
    private AnnouncementTargetType targetType;
    private List<Long> targetIds;
    private Long publisherId;
    private String publisherName;
    private LocalDateTime publishTime;
    private AnnouncementStatus status;
    private Integer readCount;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
