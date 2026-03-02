package com.openzhixue.communication.service;

import com.openzhixue.communication.dto.*;
import com.openzhixue.communication.entity.Conversation;
import com.openzhixue.communication.repository.ConversationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ConversationService {

    private final ConversationRepository conversationRepository;

    public PageResponse<ConversationResponse> getConversations(Long userId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Conversation> conversationPage = conversationRepository.findByParticipant(userId.toString(), pageable);

        List<ConversationResponse> content = conversationPage.getContent().stream()
                .map(conversation -> toConversationResponse(conversation, userId))
                .collect(Collectors.toList());

        return PageResponse.<ConversationResponse>builder()
                .content(content)
                .pageNumber(conversationPage.getNumber())
                .pageSize(conversationPage.getSize())
                .totalElements(conversationPage.getTotalElements())
                .totalPages(conversationPage.getTotalPages())
                .first(conversationPage.isFirst())
                .last(conversationPage.isLast())
                .build();
    }

    public Long getUnreadConversationCount(Long userId) {
        return conversationRepository.countUnreadConversations(userId.toString());
    }

    private ConversationResponse toConversationResponse(Conversation conversation, Long currentUserId) {
        List<Long> participants = parseParticipants(conversation.getParticipants());
        Long otherUserId = participants.stream()
                .filter(id -> !id.equals(currentUserId))
                .findFirst()
                .orElse(null);

        return ConversationResponse.builder()
                .id(conversation.getId())
                .participants(participants)
                .lastMessage(conversation.getLastMessage())
                .lastMessageType(conversation.getLastMessageType() != null ? conversation.getLastMessageType().name() : null)
                .lastMessageSenderId(conversation.getLastMessageSenderId())
                .unreadCount(conversation.getUnreadCount())
                .createdAt(conversation.getCreatedAt())
                .updatedAt(conversation.getUpdatedAt())
                .otherUserId(otherUserId)
                .build();
    }

    private List<Long> parseParticipants(String participants) {
        String cleaned = participants.replace("[", "").replace("]", "").replace(" ", "");
        return Arrays.stream(cleaned.split(","))
                .map(Long::parseLong)
                .collect(Collectors.toList());
    }
}
