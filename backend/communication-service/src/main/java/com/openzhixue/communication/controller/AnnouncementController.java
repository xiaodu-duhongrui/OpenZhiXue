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

@Tag(name = "公告管理", description = "公告发布和管理相关接口")
@RestController
@RequestMapping("/api/v1/announcements")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
public class AnnouncementController {

    private final AnnouncementService announcementService;

    @Operation(summary = "发布公告", description = "创建并发布公告")
    @PostMapping
    public ResponseEntity<ApiResponse<AnnouncementResponse>> createAnnouncement(
            @AuthenticationPrincipal Long userId,
            @RequestParam(required = false) String publisherName,
            @Valid @RequestBody CreateAnnouncementRequest request) {
        AnnouncementResponse response = announcementService.createAnnouncement(userId, publisherName, request);
        return ResponseEntity.ok(ApiResponse.success("公告创建成功", response));
    }

    @Operation(summary = "获取公告列表", description = "获取已发布的公告列表")
    @GetMapping
    public ResponseEntity<ApiResponse<PageResponse<AnnouncementResponse>>> getAnnouncements(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        PageResponse<AnnouncementResponse> response = announcementService.getAnnouncements(page, size);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "获取公告详情", description = "获取指定公告的详细信息")
    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<AnnouncementResponse>> getAnnouncement(@PathVariable Long id) {
        AnnouncementResponse response = announcementService.getAnnouncement(id);
        return ResponseEntity.ok(ApiResponse.success(response));
    }

    @Operation(summary = "删除公告", description = "删除指定的公告")
    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteAnnouncement(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long id) {
        announcementService.deleteAnnouncement(id, userId);
        return ResponseEntity.ok(ApiResponse.success("公告已删除", null));
    }

    @Operation(summary = "发布公告（草稿）", description = "将草稿状态的公告发布")
    @PutMapping("/{id}/publish")
    public ResponseEntity<ApiResponse<AnnouncementResponse>> publishAnnouncement(@PathVariable Long id) {
        AnnouncementResponse response = announcementService.publishAnnouncement(id);
        return ResponseEntity.ok(ApiResponse.success("公告已发布", response));
    }

    @Operation(summary = "获取我的公告", description = "获取当前用户发布的公告列表")
    @GetMapping("/my")
    public ResponseEntity<ApiResponse<PageResponse<AnnouncementResponse>>> getMyAnnouncements(
            @AuthenticationPrincipal Long userId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        PageResponse<AnnouncementResponse> response = announcementService.getMyAnnouncements(userId, page, size);
        return ResponseEntity.ok(ApiResponse.success(response));
    }
}
