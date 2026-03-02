package com.openzhixue.communication.repository;

import com.openzhixue.communication.entity.Message;
import com.openzhixue.communication.entity.MessageStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MessageRepository extends JpaRepository<Message, Long> {

    Page<Message> findBySenderIdOrReceiverIdOrderByCreatedAtDesc(Long senderId, Long receiverId, Pageable pageable);

    Page<Message> findByConversationIdOrderByCreatedAtDesc(Long conversationId, Pageable pageable);

    List<Message> findByReceiverIdAndStatusOrderByCreatedAtDesc(Long receiverId, MessageStatus status);

    @Query("SELECT m FROM Message m WHERE (m.senderId = :userId1 AND m.receiverId = :userId2) OR (m.senderId = :userId2 AND m.receiverId = :userId1) ORDER BY m.createdAt DESC")
    Page<Message> findConversationMessages(@Param("userId1") Long userId1, @Param("userId2") Long userId2, Pageable pageable);

    @Query("SELECT COUNT(m) FROM Message m WHERE m.receiverId = :userId AND m.status != :status")
    Long countUnreadMessages(@Param("userId") Long userId, @Param("status") MessageStatus status);

    @Modifying
    @Query("UPDATE Message m SET m.status = :status, m.readAt = CURRENT_TIMESTAMP WHERE m.receiverId = :userId AND m.senderId = :senderId AND m.status != :status")
    int markAsReadBySenderAndReceiver(@Param("userId") Long userId, @Param("senderId") Long senderId, @Param("status") MessageStatus status);

    @Modifying
    @Query("UPDATE Message m SET m.status = :status, m.readAt = CURRENT_TIMESTAMP WHERE m.id = :id")
    int markAsRead(@Param("id") Long id, @Param("status") MessageStatus status);
}
