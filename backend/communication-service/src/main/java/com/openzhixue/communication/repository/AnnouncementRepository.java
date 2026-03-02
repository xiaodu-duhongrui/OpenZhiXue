package com.openzhixue.communication.repository;

import com.openzhixue.communication.entity.Announcement;
import com.openzhixue.communication.entity.AnnouncementStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AnnouncementRepository extends JpaRepository<Announcement, Long> {

    Page<Announcement> findByStatusOrderByPublishTimeDesc(AnnouncementStatus status, Pageable pageable);

    Page<Announcement> findByPublisherIdOrderByCreatedAtDesc(Long publisherId, Pageable pageable);

    @Query("SELECT a FROM Announcement a WHERE a.status = :status AND (a.targetType = 'ALL' OR a.targetIds LIKE %:targetId%) ORDER BY a.publishTime DESC")
    Page<Announcement> findPublishedAnnouncementsForTarget(@Param("status") AnnouncementStatus status, @Param("targetId") String targetId, Pageable pageable);

    List<Announcement> findByStatusAndTargetType(AnnouncementStatus status, com.openzhixue.communication.entity.AnnouncementTargetType targetType);

    @Modifying
    @Query("UPDATE Announcement a SET a.readCount = a.readCount + 1 WHERE a.id = :id")
    int incrementReadCount(@Param("id") Long id);

    void deleteByPublisherId(Long publisherId);
}
