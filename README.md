# posts-service

## Responsibility
- Posts/comments feed domain ownership.

## Owned Domain
- Posts and comments aggregate.

## API Scope
- Public: `/api/posts*`
- Internal APIs only if required by other services (to be explicitly versioned)

## Data Ownership
- Primary schema: `stagelog_posts`

## Dependencies
- Auth context from gateway header
- May consume internal contracts from auth/events during migration

## Runtime
- API Deployment in EKS
- Shared contracts package for internal DTO/event contract compatibility
