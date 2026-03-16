package org.example.chatting.user

import jakarta.persistence.*
import org.example.chatting.common.SoftDeleteJpaEntity

@Entity
@Table(name = "users")
class UserJpaEntity(

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "username", nullable = false, unique = true)
    val username: String,

) : SoftDeleteJpaEntity() {

    @PostPersist
    fun initDeletedToken() {
        deletedToken = id.toString()
    }
}