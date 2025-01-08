# Build Stage
FROM node:18 AS builder

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY package*.json ./
RUN npm install

# 나머지 소스 코드 복사
COPY . .

# 빌드
RUN npm run build

# Production Stage
FROM node:18 AS production

# 작업 디렉토리 설정
WORKDIR /app

# 빌드된 파일만 복사
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./

# 프로덕션 의존성만 설치
RUN npm install --only=production

# 환경 변수 설정
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# 포트 노출
EXPOSE 3000

# 애플리케이션 시작 (모든 IP 주소에서 요청 수신)
CMD ["npm", "start", "--", "-H", "0.0.0.0"]
