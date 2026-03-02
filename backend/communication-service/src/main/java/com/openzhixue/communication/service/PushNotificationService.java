package com.openzhixue.communication.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.firebase.messaging.*;
import cn.jpush.api.JPushClient;
import cn.jpush.api.push.PushResult;
import cn.jpush.api.push.model.Message;
import cn.jpush.api.push.model.Platform;
import cn.jpush.api.push.model.PushPayload;
import cn.jpush.api.push.model.audience.Audience;
import cn.jpush.api.push.model.notification.AndroidNotification;
import cn.jpush.api.push.model.notification.IosNotification;
import cn.jpush.api.push.model.notification.Notification;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Slf4j
@Service
public class PushNotificationService {

    @Value("${firebase.enabled:false}")
    private boolean firebaseEnabled;

    @Value("${jpush.enabled:false}")
    private boolean jpushEnabled;

    @Value("${jpush.app-key:}")
    private String jpushAppKey;

    @Value("${jpush.master-secret:}")
    private String jpushMasterSecret;

    private final RedisTemplate<String, Object> redisTemplate;
    private final ObjectMapper objectMapper;

    private static final String DEVICE_TOKEN_PREFIX = "device:token:";
    private static final String FCM_TOKEN_PREFIX = "fcm:token:";

    public PushNotificationService(RedisTemplate<String, Object> redisTemplate, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
    }

    public void registerDeviceToken(Long userId, String deviceToken, String platform) {
        String key = DEVICE_TOKEN_PREFIX + userId;
        Map<String, String> tokenInfo = new HashMap<>();
        tokenInfo.put("token", deviceToken);
        tokenInfo.put("platform", platform);
        redisTemplate.opsForHash().putAll(key, tokenInfo);
        redisTemplate.expire(key, 30, TimeUnit.DAYS);
        log.info("Device token registered for user {}: {}", userId, deviceToken);
    }

    public void registerFcmToken(Long userId, String fcmToken) {
        String key = FCM_TOKEN_PREFIX + userId;
        redisTemplate.opsForValue().set(key, fcmToken, 30, TimeUnit.DAYS);
        log.info("FCM token registered for user {}: {}", userId, fcmToken);
    }

    public void sendPushNotification(Long userId, String title, String body) {
        sendPushNotification(userId, title, body, new HashMap<>());
    }

    public void sendPushNotification(Long userId, String title, String body, Map<String, String> data) {
        if (firebaseEnabled) {
            sendFirebasePush(userId, title, body, data);
        }

        if (jpushEnabled) {
            sendJPushNotification(userId, title, body, data);
        }

        log.info("Push notification sent to user {}: {}", userId, title);
    }

    private void sendFirebasePush(Long userId, String title, String body, Map<String, String> data) {
        try {
            String fcmToken = (String) redisTemplate.opsForValue().get(FCM_TOKEN_PREFIX + userId);
            if (fcmToken == null) {
                log.warn("No FCM token found for user {}", userId);
                return;
            }

            Message message = Message.builder()
                    .setToken(fcmToken)
                    .setNotification(com.google.firebase.messaging.Notification.builder()
                            .setTitle(title)
                            .setBody(body)
                            .build())
                    .putAllData(data)
                    .setAndroidConfig(AndroidConfig.builder()
                            .setPriority(AndroidConfig.Priority.HIGH)
                            .setNotification(AndroidNotification.builder()
                                    .setChannelId("openzhixue")
                                    .setIcon("ic_notification")
                                    .build())
                            .build())
                    .setApnsConfig(ApnsConfig.builder()
                            .setAps(Aps.builder()
                                    .setAlert(ApsAlert.builder()
                                            .setTitle(title)
                                            .setBody(body)
                                            .build())
                                    .setSound("default")
                                    .build())
                            .build())
                    .build();

            String response = FirebaseMessaging.getInstance().send(message);
            log.info("Firebase message sent successfully: {}", response);
        } catch (Exception e) {
            log.error("Failed to send Firebase push notification", e);
        }
    }

    private void sendJPushNotification(Long userId, String title, String body, Map<String, String> data) {
        try {
            JPushClient jpushClient = new JPushClient(jpushMasterSecret, jpushAppKey);

            PushPayload payload = PushPayload.newBuilder()
                    .setPlatform(Platform.android_ios())
                    .setAudience(Audience.alias(userId.toString()))
                    .setNotification(Notification.newBuilder()
                            .setAlert(body)
                            .addPlatformNotification(AndroidNotification.builder()
                                    .setTitle(title)
                                    .addExtras(data)
                                    .build())
                            .addPlatformNotification(IosNotification.builder()
                                    .incrBadge(1)
                                    .addExtras(data)
                                    .build())
                            .build())
                    .setMessage(Message.content(body))
                    .build();

            PushResult result = jpushClient.sendPush(payload);
            log.info("JPush message sent successfully: msgId={}", result.msgId);
        } catch (Exception e) {
            log.error("Failed to send JPush notification", e);
        }
    }

    public void unregisterDeviceToken(Long userId) {
        redisTemplate.delete(DEVICE_TOKEN_PREFIX + userId);
        redisTemplate.delete(FCM_TOKEN_PREFIX + userId);
        log.info("Device tokens unregistered for user {}", userId);
    }
}
