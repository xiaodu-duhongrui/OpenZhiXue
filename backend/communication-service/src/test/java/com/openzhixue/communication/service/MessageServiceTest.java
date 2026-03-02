package com.openzhixue.communication.service;

import com.openzhixue.communication.dto.SendMessageRequest;
import com.openzhixue.communication.dto.MessageResponse;
import com.openzhixue.communication.dto.PageResponse;
import com.openzhixue.communication.entity.Conversation;
import com.openzhixue.communication.entity.Message;
import com.openzhixue.communication.entity.MessageStatus;
import com.openzhixue.communication.entity.MessageType;
import com.openzhixue.communication.repository.ConversationRepository;
import com.openzhixue.communication.repository.MessageRepository;
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
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MessageServiceTest {

    @Mock
    private MessageRepository messageRepository;

    @Mock
    private ConversationRepository conversationRepository;

    @Mock
    private WebSocketMessageHandler webSocketMessageHandler;

    @InjectMocks
    private MessageService messageService;

    private Message testMessage;
    private Conversation testConversation;
    private SendMessageRequest sendRequest;

    @BeforeEach
    void setUp() {
        testMessage = Message.builder()
                .id(1L)
                .senderId(1L)
                .receiverId(2L)
                .content("Test message")
                .type(MessageType.TEXT)
                .status(MessageStatus.SENT)
                .conversationId(1L)
                .createdAt(LocalDateTime.now())
                .build();

        testConversation = Conversation.builder()
                .id(1L)
                .participants("[1, 2]")
                .unreadCount(0)
                .build();

        sendRequest = SendMessageRequest.builder()
                .receiverId(2L)
                .content("Hello")
                .type(MessageType.TEXT)
                .build();
    }

    @Test
    @DisplayName("发送消息 - 成功")
    void sendMessage_Success() {
        when(conversationRepository.findByParticipants(any(), any())).thenReturn(Optional.of(testConversation));
        when(messageRepository.save(any(Message.class))).thenReturn(testMessage);
        when(conversationRepository.save(any(Conversation.class))).thenReturn(testConversation);
        doNothing().when(webSocketMessageHandler).sendMessageToUser(anyLong(), any());

        MessageResponse response = messageService.sendMessage(1L, sendRequest);

        assertNotNull(response);
        assertEquals("Test message", response.getContent());
        verify(messageRepository, times(1)).save(any(Message.class));
        verify(webSocketMessageHandler, times(1)).sendMessageToUser(anyLong(), any());
    }

    @Test
    @DisplayName("发送消息 - 创建新会话")
    void sendMessage_CreateNewConversation() {
        when(conversationRepository.findByParticipants(any(), any())).thenReturn(Optional.empty());
        when(conversationRepository.save(any(Conversation.class))).thenReturn(testConversation);
        when(messageRepository.save(any(Message.class))).thenReturn(testMessage);
        doNothing().when(webSocketMessageHandler).sendMessageToUser(anyLong(), any());

        MessageResponse response = messageService.sendMessage(1L, sendRequest);

        assertNotNull(response);
        verify(conversationRepository, times(1)).save(any(Conversation.class));
    }

    @Test
    @DisplayName("获取消息列表 - 成功")
    void getMessages_Success() {
        Page<Message> messagePage = new PageImpl<>(Arrays.asList(testMessage));
        when(messageRepository.findBySenderIdOrReceiverIdOrderByCreatedAtDesc(anyLong(), anyLong(), any(Pageable.class)))
                .thenReturn(messagePage);

        PageResponse<MessageResponse> response = messageService.getMessages(1L, 0, 10);

        assertNotNull(response);
        assertEquals(1, response.getContent().size());
        assertEquals(1, response.getTotalElements());
    }

    @Test
    @DisplayName("获取会话消息 - 成功")
    void getConversationMessages_Success() {
        Page<Message> messagePage = new PageImpl<>(Arrays.asList(testMessage));
        when(messageRepository.findConversationMessages(anyLong(), anyLong(), any(Pageable.class)))
                .thenReturn(messagePage);
        doNothing().when(messageRepository).markAsReadBySenderAndReceiver(anyLong(), anyLong(), any());

        PageResponse<MessageResponse> response = messageService.getConversationMessages(1L, 2L, 0, 10);

        assertNotNull(response);
        assertEquals(1, response.getContent().size());
        verify(messageRepository, times(1)).markAsReadBySenderAndReceiver(anyLong(), anyLong(), any());
    }

    @Test
    @DisplayName("标记消息已读 - 成功")
    void markAsRead_Success() {
        when(messageRepository.findById(1L)).thenReturn(Optional.of(testMessage));
        when(messageRepository.save(any(Message.class))).thenReturn(testMessage);
        doNothing().when(webSocketMessageHandler).sendReadReceipt(anyLong(), anyLong());

        assertDoesNotThrow(() -> messageService.markAsRead(1L, 2L));

        verify(messageRepository, times(1)).save(any(Message.class));
        verify(webSocketMessageHandler, times(1)).sendReadReceipt(anyLong(), anyLong());
    }

    @Test
    @DisplayName("标记消息已读 - 消息不存在")
    void markAsRead_MessageNotFound() {
        when(messageRepository.findById(1L)).thenReturn(Optional.empty());

        assertThrows(RuntimeException.class, () -> messageService.markAsRead(1L, 2L));
    }

    @Test
    @DisplayName("标记消息已读 - 无权限")
    void markAsRead_Unauthorized() {
        when(messageRepository.findById(1L)).thenReturn(Optional.of(testMessage));

        assertThrows(RuntimeException.class, () -> messageService.markAsRead(1L, 3L));
    }

    @Test
    @DisplayName("获取未读消息数 - 成功")
    void getUnreadCount_Success() {
        when(messageRepository.countUnreadMessages(anyLong(), any())).thenReturn(5L);

        Long count = messageService.getUnreadCount(1L);

        assertEquals(5L, count);
        verify(messageRepository, times(1)).countUnreadMessages(anyLong(), any());
    }
}
