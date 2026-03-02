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
@Table(name = "conversations", indexes = {
    @Index(name = "idx_conversation_updated", columnList = "updatedAt")
})
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@EntityListeners(AuditingEntityListener.class)
public class Conversation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String participants;

    @Column(columnDefinition = "TEXT")
    private String lastMessage;

    @Enumerated(EnumType.STRING)
    private MessageType lastMessageType;

    private Long lastMessageSenderId;

    @Column(nullable = false)
    @Builder.Default
    private Integer unreadCount = 0;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    public void updateLastMessage(String message, MessageType type, Long senderId) {
        this.lastMessage = message;
        this.lastMessageType = type;
        this.lastMessageSenderId = senderId;
        this.updatedAt = LocalDateTime.now();
    }

    public void incrementUnreadCount() {
        this.unreadCount++;
    }

    public void resetUnreadCount() {
        this.unreadCount = 0;
    }
}
