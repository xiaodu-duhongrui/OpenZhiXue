package com.openzhixue.communication.service;

import com.openzhixue.communication.dto.NotificationResponse;
import com.openzhixue.communication.dto.PageResponse;
import com.openzhixue.communication.dto.SendNotificationRequest;
import com.openzhixue.communication.entity.Notification;
import com.openzhixue.communication.entity.NotificationType;
import com.openzhixue.communication.repository.NotificationRepository;
import com.openzhixue.communication.websocket.WebSocketMessageHandler;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class NotificationServiceTest {

    @Mock
    private NotificationRepository notificationRepository;

    @Mock
    private PushNotificationService pushNotificationService;

    @Mock
    private WebSocketMessageHandler webSocketMessageHandler;

    @InjectMocks
    private NotificationService notificationService;

    private Notification testNotification;
    private SendNotificationRequest sendRequest;

    @BeforeEach
    void setUp() {
        testNotification = Notification.builder()
                .id(1L)
                .userId(1L)
                .title("Test Title")
                .content("Test Content")
                .type(NotificationType.SYSTEM)
                .isRead(false)
                .createdAt(LocalDateTime.now())
                .build();

        sendRequest = SendNotificationRequest.builder()
                .userId(1L)
                .title("New Notification")
                .content("Notification Content")
                .type(NotificationType.SYSTEM)
                .build();
    }

    @Test
    @DisplayName("发送通知 - 成功")
    void sendNotification_Success() {
        when(notificationRepository.save(any(Notification.class))).thenReturn(testNotification);
        doNothing().when(webSocketMessageHandler).sendNotificationToUser(anyLong(), any());
        doNothing().when(pushNotificationService).sendPushNotification(anyLong(), any(), any());

        NotificationResponse response = notificationService.sendNotification(sendRequest);

        assertNotNull(response);
        assertEquals("Test Title", response.getTitle());
        verify(notificationRepository, times(1)).save(any(Notification.class));
        verify(webSocketMessageHandler, times(1)).sendNotificationToUser(anyLong(), any());
        verify(pushNotificationService, times(1)).sendPushNotification(anyLong(), any(), any());
    }

    @Test
    @DisplayName("获取通知列表 - 成功")
    void getNotifications_Success() {
        Page<Notification> notificationPage = new PageImpl<>(Arrays.asList(testNotification));
        when(notificationRepository.findByUserIdOrderByCreatedAtDesc(anyLong(), any(Pageable.class)))
                .thenReturn(notificationPage);

        PageResponse<NotificationResponse> response = notificationService.getNotifications(1L, 0, 10);

        assertNotNull(response);
        assertEquals(1, response.getContent().size());
        assertEquals(1, response.getTotalElements());
    }

    @Test
    @DisplayName("获取通知列表 - 空列表")
    void getNotifications_EmptyList() {
        Page<Notification> emptyPage = new PageImpl<>(Arrays.asList());
        when(notificationRepository.findByUserIdOrderByCreatedAtDesc(anyLong(), any(Pageable.class)))
                .thenReturn(emptyPage);

        PageResponse<NotificationResponse> response = notificationService.getNotifications(1L, 0, 10);

        assertNotNull(response);
        assertTrue(response.getContent().isEmpty());
        assertEquals(0, response.getTotalElements());
    }

    @Test
    @DisplayName("标记通知已读 - 成功")
    void markAsRead_Success() {
        when(notificationRepository.findById(1L)).thenReturn(Optional.of(testNotification));
        when(notificationRepository.save(any(Notification.class))).thenReturn(testNotification);

        assertDoesNotThrow(() -> notificationService.markAsRead(1L, 1L));

        verify(notificationRepository, times(1)).save(any(Notification.class));
    }

    @Test
    @DisplayName("标记通知已读 - 通知不存在")
    void markAsRead_NotificationNotFound() {
        when(notificationRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(RuntimeException.class, () -> notificationService.markAsRead(1L, 1L));
    }

    @Test
    @DisplayName("标记通知已读 - 无权限")
    void markAsRead_Unauthorized() {
        when(notificationRepository.findById(1L)).thenReturn(Optional.of(testNotification));

        assertThrows(RuntimeException.class, () -> notificationService.markAsRead(1L, 2L));
    }

    @Test
    @DisplayName("标记所有通知已读 - 成功")
    void markAllAsRead_Success() {
        doNothing().when(notificationRepository).markAllAsRead(anyLong());

        assertDoesNotThrow(() -> notificationService.markAllAsRead(1L));

        verify(notificationRepository, times(1)).markAllAsRead(1L);
    }

    @Test
    @DisplayName("获取未读通知数 - 成功")
    void getUnreadCount_Success() {
        when(notificationRepository.countUnreadNotifications(anyLong())).thenReturn(3L);

        Long count = notificationService.getUnreadCount(1L);

        assertEquals(3L, count);
        verify(notificationRepository, times(1)).countUnreadNotifications(1L);
    }
}
