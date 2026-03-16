package org.example.chatting.common

import jakarta.persistence.Column
import jakarta.persistence.MappedSuperclass
import java.time.Instant

@MappedSuperclass
abstract class SoftDeleteJpaEntity : AuditJpaEntity(createdAt = Instant.now(), updatedAt = Instant.now()) {

    @Column(name = "deleted_token")
    var deletedToken: String? = null

    @Column(name = "deleted_at")
    var deletedAt: Instant? = null

    fun softDelete(deletedToken: String) {
        this.deletedToken = deletedToken
        this.deletedAt = Instant.now()
    }
}