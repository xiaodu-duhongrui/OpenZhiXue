package com.openzhixue.communication.controller;

import com.openzhixue.communication.service.PushNotificationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Tag(name = "设备管理", description = "设备注册和推送相关接口")
@RestController
@RequestMapping("/api/v1/devices")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
public class DeviceController {

    private final PushNotificationService pushNotificationService;

    @Operation(summary = "注册设备Token", description = "注册设备推送Token")
    @PostMapping("/register")
    public ResponseEntity<Map<String, String>> registerDevice(
            @AuthenticationPrincipal Long userId,
            @RequestBody Map<String, String> request) {
        String deviceToken = request.get("deviceToken");
        String platform = request.getOrDefault("platform", "android");
        pushNotificationService.registerDeviceToken(userId, deviceToken, platform);
        return ResponseEntity.ok(Map.of("message", "设备注册成功"));
    }

    @Operation(summary = "注册FCM Token", description = "注册Firebase Cloud Messaging Token")
    @PostMapping("/register-fcm")
    public ResponseEntity<Map<String, String>> registerFcmToken(
            @AuthenticationPrincipal Long userId,
            @RequestBody Map<String, String> request) {
        String fcmToken = request.get("fcmToken");
        pushNotificationService.registerFcmToken(userId, fcmToken);
        return ResponseEntity.ok(Map.of("message", "FCM Token注册成功"));
    }

    @Operation(summary = "注销设备", description = "注销设备推送Token")
    @DeleteMapping("/unregister")
    public ResponseEntity<Map<String, String>> unregisterDevice(@AuthenticationPrincipal Long userId) {
        pushNotificationService.unregisterDeviceToken(userId);
        return ResponseEntity.ok(Map.of("message", "设备注销成功"));
    }
}
