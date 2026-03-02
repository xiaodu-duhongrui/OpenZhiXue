package com.openzhixue.communication.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "announcements", indexes = {
    @Index(name = "idx_announcement_publisher", columnList = "publisherId"),
    @Index(name = "idx_announcement_status", columnList = "status"),
    @Index(name = "idx_announcement_publish_time", columnList = "publishTime")
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
public class Announcement {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String content;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AnnouncementTargetType targetType;

    @Column(columnDefinition = "TEXT")
    private String targetIds;

    @Column(nullable = false)
    private Long publisherId;

    private String publisherName;

    private LocalDateTime publishTime;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private AnnouncementStatus status = AnnouncementStatus.DRAFT;

    private Integer readCount;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    public void publish() {
        this.status = AnnouncementStatus.PUBLISHED;
        this.publishTime = LocalDateTime.now();
    }

    public void revoke() {
        this.status = AnnouncementStatus.REVOKED;
    }
}
