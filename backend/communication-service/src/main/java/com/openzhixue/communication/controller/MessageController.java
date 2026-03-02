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

@Tag(name = "消息管理", description = "消息发送和接收相关接口")
@RestController
@RequestMapping("/api/v1/messages")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
public class MessageController {

    private final MessageService messageService;

    @Operation(summary = "发送消息", description = "发送消息给指定用户")
    @PostMapping
    public ResponseEntity<ApiResponse<MessageResponse>> sendMessage(
            @AuthenticationPrincipal Long userId,
            @Valid @RequestBody SendMessageRequest request) {
        MessageResponse response = messageService.sendMessage(userId, request);
        return ResponseEntity.ok(ApiResponse.success("消息发送成功", response));
    }

    @Operation(summary = "获取消息列表", description = "获取当前用户的所有消息")
    @GetMapping
    public ResponseEntity<ApiResponse<PageResponse<MessageResponse>>> getMessages(
            @AuthenticationPrincipal Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageResponse<MessageResponse> response = messageService.getMessages(userId, page, size);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "标记消息已读", description = "将指定消息标记为已读")
    @PutMapping("/{id}/read")
    public ResponseEntity<ApiResponse<Void>> markAsRead(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long id) {
        messageService.markAsRead(id, userId);
        return ResponseEntity.ok(ApiResponse.success("已标记为已读", null));
    }

    @Operation(summary = "获取未读消息数量", description = "获取当前用户的未读消息数量")
    @GetMapping("/unread-count")
    public ResponseEntity<ApiResponse<Long>> getUnreadCount(@AuthenticationPrincipal Long userId) {
        Long count = messageService.getUnreadCount(userId);
        return ResponseEntity.ok(ApiResponse.success(count));
    }
}
