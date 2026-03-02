package com.openzhixue.communication.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.openzhixue.communication.dto.*;
import com.openzhixue.communication.entity.*;
import com.openzhixue.communication.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class AnnouncementService {

    private final AnnouncementRepository announcementRepository;
    private final NotificationService notificationService;
    private final ObjectMapper objectMapper;

    @Transactional
    public AnnouncementResponse createAnnouncement(Long publisherId, String publisherName, CreateAnnouncementRequest request) {
        Announcement announcement = Announcement.builder()
                .title(request.getTitle())
                .content(request.getContent())
                .targetType(request.getTargetType())
                .targetIds(serializeTargetIds(request.getTargetIds()))
                .publisherId(publisherId)
                .publisherName(publisherName)
                .readCount(0)
                .build();

        if (request.isPublishImmediately()) {
            announcement.publish();
        }

        announcement = announcementRepository.save(announcement);

        if (announcement.getStatus() == AnnouncementStatus.PUBLISHED) {
            notifyTargetUsers(announcement);
        }

        log.info("Announcement created: {}", announcement.getId());
        return toAnnouncementResponse(announcement);
    }

    @Transactional
    public AnnouncementResponse publishAnnouncement(Long announcementId) {
        Announcement announcement = announcementRepository.findById(announcementId)
                .orElseThrow(() -> new RuntimeException("公告不存在"));

        if (announcement.getStatus() != AnnouncementStatus.DRAFT) {
            throw new RuntimeException("只能发布草稿状态的公告");
        }

        announcement.publish();
        announcement = announcementRepository.save(announcement);

        notifyTargetUsers(announcement);

        log.info("Announcement published: {}", announcementId);
        return toAnnouncementResponse(announcement);
    }

    public PageResponse<AnnouncementResponse> getAnnouncements(int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Announcement> announcementPage = announcementRepository.findByStatusOrderByPublishTimeDesc(AnnouncementStatus.PUBLISHED, pageable);

        List<AnnouncementResponse> content = announcementPage.getContent().stream()
                .map(this::toAnnouncementResponse)
                .collect(Collectors.toList());

        return PageResponse.<AnnouncementResponse>builder()
                .content(content)
                .pageNumber(announcementPage.getNumber())
                .pageSize(announcementPage.getSize())
                .totalElements(announcementPage.getTotalElements())
                .totalPages(announcementPage.getTotalPages())
                .first(announcementPage.isFirst())
                .last(announcementPage.isLast())
                .build();
    }

    public AnnouncementResponse getAnnouncement(Long id) {
        Announcement announcement = announcementRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("公告不存在"));

        announcementRepository.incrementReadCount(id);

        return toAnnouncementResponse(announcement);
    }

    @Transactional
    public void deleteAnnouncement(Long id, Long publisherId) {
        Announcement announcement = announcementRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("公告不存在"));

        if (!announcement.getPublisherId().equals(publisherId)) {
            throw new RuntimeException("无权删除此公告");
        }

        announcementRepository.delete(announcement);
        log.info("Announcement deleted: {}", id);
    }

    public PageResponse<AnnouncementResponse> getMyAnnouncements(Long publisherId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Announcement> announcementPage = announcementRepository.findByPublisherIdOrderByCreatedAtDesc(publisherId, pageable);

        List<AnnouncementResponse> content = announcementPage.getContent().stream()
                .map(this::toAnnouncementResponse)
                .collect(Collectors.toList());

        return PageResponse.<AnnouncementResponse>builder()
                .content(content)
                .pageNumber(announcementPage.getNumber())
                .pageSize(announcementPage.getSize())
                .totalElements(announcementPage.getTotalElements())
                .totalPages(announcementPage.getTotalPages())
                .first(announcementPage.isFirst())
                .last(announcementPage.isLast())
                .build();
    }

    private void notifyTargetUsers(Announcement announcement) {
        // TODO: 根据目标类型获取目标用户列表并发送通知
        log.info("Notifying target users for announcement: {}", announcement.getId());
    }

    private String serializeTargetIds(List<Long> targetIds) {
        if (targetIds == null || targetIds.isEmpty()) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(targetIds);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize target ids", e);
            return null;
        }
    }

    private List<Long> deserializeTargetIds(String targetIds) {
        if (targetIds == null || targetIds.isEmpty()) {
            return Collections.emptyList();
        }
        try {
            return objectMapper.readValue(targetIds, new TypeReference<List<Long>>() {});
        } catch (JsonProcessingException e) {
            log.error("Failed to deserialize target ids", e);
            return Collections.emptyList();
        }
    }

    private AnnouncementResponse toAnnouncementResponse(Announcement announcement) {
        return AnnouncementResponse.builder()
                .id(announcement.getId())
                .title(announcement.getTitle())
                .content(announcement.getContent())
                .targetType(announcement.getTargetType())
                .targetIds(deserializeTargetIds(announcement.getTargetIds()))
                .publisherId(announcement.getPublisherId())
                .publisherName(announcement.getPublisherName())
                .publishTime(announcement.getPublishTime())
                .status(announcement.getStatus())
                .readCount(announcement.getReadCount())
                .createdAt(announcement.getCreatedAt())
                .updatedAt(announcement.getUpdatedAt())
                .build();
    }
}
