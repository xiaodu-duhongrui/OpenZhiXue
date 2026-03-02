package com.openzhixue.communication.repository;

import com.openzhixue.communication.entity.Conversation;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ConversationRepository extends JpaRepository<Conversation, Long> {

    @Query("SELECT c FROM Conversation c WHERE c.participants LIKE %:participant1% AND c.participants LIKE %:participant2%")
    Optional<Conversation> findByParticipants(@Param("participant1") String participant1, @Param("participant2") String participant2);

    @Query("SELECT c FROM Conversation c WHERE c.participants LIKE %:userId% ORDER BY c.updatedAt DESC")
    Page<Conversation> findByParticipant(@Param("userId") String userId, Pageable pageable);

    @Query("SELECT COUNT(c) FROM Conversation c WHERE c.participants LIKE %:userId% AND c.unreadCount > 0")
    Long countUnreadConversations(@Param("userId") String userId);
}
