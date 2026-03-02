package com.openzhixue.communication.service;

import com.openzhixue.communication.dto.*;
import com.openzhixue.communication.entity.Notification;
import com.openzhixue.communication.repository.NotificationRepository;
import com.openzhixue.communication.websocket.WebSocketMessageHandler;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationRepository notificationRepository;
    private final PushNotificationService pushNotificationService;
    private final WebSocketMessageHandler webSocketMessageHandler;

    @Transactional
    public NotificationResponse sendNotification(SendNotificationRequest request) {
        Notification notification = Notification.builder()
                .userId(request.getUserId())
                .title(request.getTitle())
                .content(request.getContent())
                .type(request.getType())
                .relatedId(request.getRelatedId())
                .relatedType(request.getRelatedType())
                .build();

        notification = notificationRepository.save(notification);

        NotificationResponse response = toNotificationResponse(notification);

        webSocketMessageHandler.sendNotificationToUser(request.getUserId(), response);

        pushNotificationService.sendPushNotification(
                request.getUserId(),
                request.getTitle(),
                request.getContent()
        );

        log.info("Notification sent to user {}", request.getUserId());
        return response;
    }

    public PageResponse<NotificationResponse> getNotifications(Long userId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Notification> notificationPage = notificationRepository.findByUserIdOrderByCreatedAtDesc(userId, pageable);

        List<NotificationResponse> content = notificationPage.getContent().stream()
                .map(this::toNotificationResponse)
                .collect(Collectors.toList());

        return PageResponse.<NotificationResponse>builder()
                .content(content)
                .pageNumber(notificationPage.getNumber())
                .pageSize(notificationPage.getSize())
                .totalElements(notificationPage.getTotalElements())
                .totalPages(notificationPage.getTotalPages())
                .first(notificationPage.isFirst())
                .last(notificationPage.isLast())
                .build();
    }

    @Transactional
    public void markAsRead(Long notificationId, Long userId) {
        Notification notification = notificationRepository.findById(notificationId)
                .orElseThrow(() -> new RuntimeException("通知不存在"));

        if (!notification.getUserId().equals(userId)) {
            throw new RuntimeException("无权操作此通知");
        }

        notification.markAsRead();
        notificationRepository.save(notification);
    }

    @Transactional
    public void markAllAsRead(Long userId) {
        notificationRepository.markAllAsRead(userId);
    }

    public Long getUnreadCount(Long userId) {
        return notificationRepository.countUnreadNotifications(userId);
    }

    private NotificationResponse toNotificationResponse(Notification notification) {
        return NotificationResponse.builder()
                .id(notification.getId())
                .userId(notification.getUserId())
                .title(notification.getTitle())
                .content(notification.getContent())
                .type(notification.getType())
                .isRead(notification.getIsRead())
                .relatedId(notification.getRelatedId())
                .relatedType(notification.getRelatedType())
                .createdAt(notification.getCreatedAt())
                .readAt(notification.getReadAt())
                .build();
    }
}
