package com.openzhixue.communication.service;

import com.openzhixue.communication.dto.*;
import com.openzhixue.communication.entity.*;
import com.openzhixue.communication.repository.*;
import com.openzhixue.communication.websocket.WebSocketMessageHandler;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class MessageService {

    private final MessageRepository messageRepository;
    private final ConversationRepository conversationRepository;
    private final WebSocketMessageHandler webSocketMessageHandler;

    @Transactional
    public MessageResponse sendMessage(Long senderId, SendMessageRequest request) {
        Conversation conversation = getOrCreateConversation(senderId, request.getReceiverId());

        Message message = Message.builder()
                .senderId(senderId)
                .receiverId(request.getReceiverId())
                .content(request.getContent())
                .type(request.getType())
                .status(MessageStatus.SENT)
                .conversationId(conversation.getId())
                .attachmentUrl(request.getAttachmentUrl())
                .attachmentName(request.getAttachmentName())
                .attachmentSize(request.getAttachmentSize())
                .build();

        message = messageRepository.save(message);

        conversation.updateLastMessage(request.getContent(), request.getType(), senderId);
        if (!senderId.equals(request.getReceiverId())) {
            conversation.incrementUnreadCount();
        }
        conversationRepository.save(conversation);

        MessageResponse response = toMessageResponse(message);
        webSocketMessageHandler.sendMessageToUser(request.getReceiverId(), response);

        log.info("Message sent from {} to {}", senderId, request.getReceiverId());
        return response;
    }

    public PageResponse<MessageResponse> getMessages(Long userId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Message> messagePage = messageRepository.findBySenderIdOrReceiverIdOrderByCreatedAtDesc(userId, userId, pageable);

        List<MessageResponse> content = messagePage.getContent().stream()
                .map(this::toMessageResponse)
                .collect(Collectors.toList());

        return PageResponse.<MessageResponse>builder()
                .content(content)
                .pageNumber(messagePage.getNumber())
                .pageSize(messagePage.getSize())
                .totalElements(messagePage.getTotalElements())
                .totalPages(messagePage.getTotalPages())
                .first(messagePage.isFirst())
                .last(messagePage.isLast())
                .build();
    }

    public PageResponse<MessageResponse> getConversationMessages(Long userId, Long otherUserId, int page, int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Message> messagePage = messageRepository.findConversationMessages(userId, otherUserId, pageable);

        messageRepository.markAsReadBySenderAndReceiver(userId, otherUserId, MessageStatus.READ);

        List<MessageResponse> content = messagePage.getContent().stream()
                .map(this::toMessageResponse)
                .collect(Collectors.toList());

        return PageResponse.<MessageResponse>builder()
                .content(content)
                .pageNumber(messagePage.getNumber())
                .pageSize(messagePage.getSize())
                .totalElements(messagePage.getTotalElements())
                .totalPages(messagePage.getTotalPages())
                .first(messagePage.isFirst())
                .last(messagePage.isLast())
                .build();
    }

    @Transactional
    public void markAsRead(Long messageId, Long userId) {
        Message message = messageRepository.findById(messageId)
                .orElseThrow(() -> new RuntimeException("消息不存在"));

        if (!message.getReceiverId().equals(userId)) {
            throw new RuntimeException("无权操作此消息");
        }

        message.markAsRead();
        messageRepository.save(message);

        webSocketMessageHandler.sendReadReceipt(message.getSenderId(), messageId);
    }

    public Long getUnreadCount(Long userId) {
        return messageRepository.countUnreadMessages(userId, MessageStatus.READ);
    }

    private Conversation getOrCreateConversation(Long userId1, Long userId2) {
        String participantKey = createParticipantKey(userId1, userId2);
        Optional<Conversation> existingConversation = conversationRepository.findByParticipants(participantKey, participantKey);

        if (existingConversation.isPresent()) {
            return existingConversation.get();
        }

        Conversation conversation = Conversation.builder()
                .participants(participantKey)
                .unreadCount(0)
                .build();
        return conversationRepository.save(conversation);
    }

    private String createParticipantKey(Long userId1, Long userId2) {
        Long[] ids = {userId1, userId2};
        Arrays.sort(ids);
        return Arrays.toString(ids);
    }

    private MessageResponse toMessageResponse(Message message) {
        return MessageResponse.builder()
                .id(message.getId())
                .senderId(message.getSenderId())
                .receiverId(message.getReceiverId())
                .content(message.getContent())
                .type(message.getType())
                .status(message.getStatus())
                .conversationId(message.getConversationId())
                .attachmentUrl(message.getAttachmentUrl())
                .attachmentName(message.getAttachmentName())
                .attachmentSize(message.getAttachmentSize())
                .createdAt(message.getCreatedAt())
                .readAt(message.getReadAt())
                .build();
    }
}
