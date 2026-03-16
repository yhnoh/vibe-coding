### JPA 컨벤션

- 엔티티 클래스는 접미사에 `JpaEntity`를 붙여서 명명한다. 예: `UserJpaEntity`, `ProductJpaEntity`
- 리포지토리는 접미사에 `JpaRepository`를 붙여서 명명한다. 예: `UserJpaRepository`, `ProductJpaRepository`
- @Column 어노테이션에 name 속성을 명시하며, 컬럼 이름은 소문자와 언더스코어(_)로 구성한다. 예: `@Column(name = "created_at")`