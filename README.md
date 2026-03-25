# Posts Service

`posts`는 게시글, 댓글, 이미지 업로드를 담당하는 Django 서비스입니다.

## Responsibility
- 게시글/댓글 조회 및 작성
- 공연별 게시글 피드 제공
- 게시글 이미지 업로드용 presign URL 발급
- 알림용 outbox 이벤트 발행

## Main Routes
- Public
  - `/api/posts*`
- Internal
  - 별도 내부 API는 최소화하고, 필요한 경우에만 명시적으로 추가합니다

## Runtime
- Python 3.12 / Django / Gunicorn
- 컨테이너 포트: `8000`
- Kubernetes에서는 Secret key를 환경변수로 직접 주입합니다

## Deploy
- Kubernetes 매니페스트
  - [`posts/deploy/k8s/posts-env-externalsecret.yaml`](/home/woosupar/stagelog/posts/deploy/k8s/posts-env-externalsecret.yaml)
  - [`posts/deploy/k8s/posts-serviceaccount.yaml`](/home/woosupar/stagelog/posts/deploy/k8s/posts-serviceaccount.yaml)
  - [`posts/deploy/k8s/posts-deployment.yaml`](/home/woosupar/stagelog/posts/deploy/k8s/posts-deployment.yaml)
- CI/CD workflow
  - [`posts/.github/workflows/build-and-push.yml`](/home/woosupar/stagelog/posts/.github/workflows/build-and-push.yml)

배포 흐름은 아래와 같습니다.
- GitHub Actions가 이미지를 빌드해 ECR에 push
- 같은 workflow가 `stagelog-gitops`의 이미지 태그를 갱신
- ArgoCD가 변경된 태그를 감지해 클러스터에 반영

## Configuration
주요 환경변수 예시는 [`posts/.env.example`](/home/woosupar/stagelog/posts/.env.example) 에 있습니다.

운영 환경에서는 SSM Parameter Store를 소스 오브 트루스로 사용하고, ExternalSecret이 필요한 키만 Kubernetes Secret으로 동기화합니다.

## Notes
- S3 presign 기능 때문에 전용 IRSA 권한이 필요합니다.
- 공연별 게시글 조회/작성 경로는 기존 `events` 하위 경로에서 `posts` 서비스 경로로 이관된 상태입니다.
- 보호 라우트에서는 API Gateway가 전달한 `X-User-Id` 헤더를 사용자 문맥으로 사용합니다.
