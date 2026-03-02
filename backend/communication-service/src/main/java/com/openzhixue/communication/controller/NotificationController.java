package com.openzhixue.communication.controller;

import com.openzhixue.communication.dto.*;
import com.openzhixue.communication.service.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Tag(name = "通知管理", description = "通知推送相关接口")
@RestController
@RequestMapping("/api/v1/notifications")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
public class NotificationController {

    private final NotificationService notificationService;

    @Operation(summary = "发送通知", description = "向指定用户发送通知")
    @PostMapping
    public ResponseEntity<ApiResponse<NotificationResponse>> sendNotification(
            @Valid @RequestBody SendNotificationRequest request) {
        NotificationResponse response = notificationService.sendNotification(request);
        return ResponseEntity.ok(ApiResponse.success("通知发送成功", response));
    }

    @Operation(summary = "获取通知列表", description = "获取当前用户的通知列表")
    @GetMapping
    public ResponseEntity<ApiResponse<PageResponse<NotificationResponse>>> getNotifications(
            @AuthenticationPrincipal Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageResponse<NotificationResponse> response = notificationService.getNotifications(userId, page, size);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "标记通知已读", description = "将指定通知标记为已读")
    @PutMapping("/{id}/read")
    public ResponseEntity<ApiResponse<Void>> markAsRead(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long id) {
        notificationService.markAsRead(id, userId);
        return ResponseEntity.ok(ApiResponse.success("已标记为已读", null));
    }

    @Operation(summary = "标记所有通知已读", description = "将当前用户的所有通知标记为已读")
    @PutMapping("/read-all")
    public ResponseEntity<ApiResponse<Void>> markAllAsRead(@AuthenticationPrincipal Long userId) {
        notificationService.markAllAsRead(userId);
        return ResponseEntity.ok(ApiResponse.success("已全部标记为已读", null));
    }

    @Operation(summary = "获取未读通知数量", description = "获取当前用户的未读通知数量")
    @GetMapping("/unread-count")
    public ResponseEntity<ApiResponse<Long>> getUnreadCount(@AuthenticationPrincipal Long userId) {
        Long count = notificationService.getUnreadCount(userId);
        return ResponseEntity.ok(ApiResponse.success(count));
    }
}
