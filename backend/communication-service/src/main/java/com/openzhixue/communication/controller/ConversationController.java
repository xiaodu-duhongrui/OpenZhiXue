package com.openzhixue.communication.controller;

import com.openzhixue.communication.dto.*;
import com.openzhixue.communication.service.*;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@Tag(name = "会话管理", description = "会话列表相关接口")
@RestController
@RequestMapping("/api/v1/conversations")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
public class ConversationController {

    private final ConversationService conversationService;
    private final MessageService messageService;

    @Operation(summary = "获取会话列表", description = "获取当前用户的所有会话")
    @GetMapping
    public ResponseEntity<ApiResponse<PageResponse<ConversationResponse>>> getConversations(
            @AuthenticationPrincipal Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageResponse<ConversationResponse> response = conversationService.getConversations(userId, page, size);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取会话消息", description = "获取指定会话的消息列表")
    @GetMapping("/{otherUserId}/messages")
    public ResponseEntity<ApiResponse<PageResponse<MessageResponse>>> getConversationMessages(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long otherUserId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        PageResponse<MessageResponse> response = messageService.getConversationMessages(userId, otherUserId, page, size);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取未读会话数量", description = "获取当前用户的未读会话数量")
    @GetMapping("/unread-count")
    public ResponseEntity<ApiResponse<Long>> getUnreadCount(@AuthenticationPrincipal Long userId) {
        Long count = conversationService.getUnreadConversationCount(userId);
        return ResponseEntity.ok(ApiResponse.success(count));
    }
}
