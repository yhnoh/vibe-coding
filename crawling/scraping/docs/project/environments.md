# 환경 설정

## 현재 상태

환경 분리 미구현. 모든 설정이 하드코딩되어 있음.

## 환경 목록

| 환경 | 용도 | 인프라 |
|------|------|--------|
| local | 개발 | 로컬 PC |
| dev | 개발 서버 | AWS ECS Fargate |
| prod | 운영 | AWS ECS Fargate + ELB |

## 인프라 구성

```
[ELB] → [ECS Fargate] → [NAT Gateway] → 인터넷
                                        (또는 Decodo 프록시)
```

- AWS ECS Fargate: 컨테이너 실행
- ELB: 인바운드 로드밸런싱
- NAT Gateway: 아웃바운드 (고정 IP)
- Decodo 프록시: IP 차단 대비 (미적용)

## AWS 자격증명

| 환경 | 방식 |
|------|------|
| local | `~/.aws/credentials` (프로필별 전환: `AWS_PROFILE=dev`) |
| ECS Fargate | IAM Task Role (코드 변경 없이 자동 적용) |

## 향후 환경 분리 방안

### Scrapy
```bash
SCRAPY_SETTINGS_MODULE=scrapying.settings_dev uv run scrapy crawl <spider>
```

### FastAPI
```bash
ENV=dev make api
```

## TODO
- [ ] settings 파일 환경별 분리
- [ ] 환경변수로 S3 버킷, DB 접속 정보 관리
- [ ] Dockerfile에 환경변수 주입 설정
