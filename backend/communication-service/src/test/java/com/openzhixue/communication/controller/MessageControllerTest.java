package com.openzhixue.communication.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.openzhixue.communication.dto.SendMessageRequest;
import com.openzhixue.communication.dto.MessageResponse;
import com.openzhixue.communication.dto.PageResponse;
import com.openzhixue.communication.entity.MessageType;
import com.openzhixue.communication.service.MessageService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.Arrays;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(MessageController.class)
class MessageControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private MessageService messageService;

    private MessageResponse testMessageResponse;
    private PageResponse<MessageResponse> testPageResponse;

    @BeforeEach
    void setUp() {
        testMessageResponse = MessageResponse.builder()
                .id(1L)
                .senderId(1L)
                .receiverId(2L)
                .content("Test message")
                .type(MessageType.TEXT)
                .createdAt(LocalDateTime.now())
                .build();

        testPageResponse = PageResponse.<MessageResponse>builder()
                .content(Arrays.asList(testMessageResponse))
                .pageNumber(0)
                .pageSize(10)
                .totalElements(1L)
                .totalPages(1)
                .first(true)
                .last(true)
                .build();
    }

    @Test
    @DisplayName("发送消息 - 成功")
    @WithMockUser(username = "1")
    void sendMessage_Success() throws Exception {
        SendMessageRequest request = SendMessageRequest.builder()
                .receiverId(2L)
                .content("Hello")
                .type(MessageType.TEXT)
                .build();

        when(messageService.sendMessage(anyLong(), any())).thenReturn(testMessageResponse);

        mockMvc.perform(post("/api/messages/send")
                        .with(csrf())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.content").value("Test message"));
    }

    @Test
    @DisplayName("获取消息列表 - 成功")
    @WithMockUser(username = "1")
    void getMessages_Success() throws Exception {
        when(messageService.getMessages(anyLong(), anyInt(), anyInt())).thenReturn(testPageResponse);

        mockMvc.perform(get("/api/messages")
                        .param("page", "0")
                        .param("size", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.content").isArray())
                .andExpect(jsonPath("$.data.content[0].content").value("Test message"));
    }

    @Test
    @DisplayName("获取会话消息 - 成功")
    @WithMockUser(username = "1")
    void getConversationMessages_Success() throws Exception {
        when(messageService.getConversationMessages(anyLong(), anyLong(), anyInt(), anyInt()))
                .thenReturn(testPageResponse);

        mockMvc.perform(get("/api/messages/conversation/2")
                        .param("page", "0")
                        .param("size", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.content").isArray());
    }

    @Test
    @DisplayName("标记消息已读 - 成功")
    @WithMockUser(username = "1")
    void markAsRead_Success() throws Exception {
        mockMvc.perform(post("/api/messages/1/read")
                        .with(csrf()))
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("获取未读消息数 - 成功")
    @WithMockUser(username = "1")
    void getUnreadCount_Success() throws Exception {
        when(messageService.getUnreadCount(anyLong())).thenReturn(5L);

        mockMvc.perform(get("/api/messages/unread-count"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data").value(5));
    }

    @Test
    @DisplayName("发送消息 - 未授权")
    void sendMessage_Unauthorized() throws Exception {
        SendMessageRequest request = SendMessageRequest.builder()
                .receiverId(2L)
                .content("Hello")
                .type(MessageType.TEXT)
                .build();

        mockMvc.perform(post("/api/messages/send")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized());
    }
}
