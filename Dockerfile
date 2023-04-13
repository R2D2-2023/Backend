FROM postgres:11 
ENV POSTGRES_PASSWORD: postgres
ENV POSTGRES_USER: postgres
ENV POSTGRES_DB: postgres
EXPOSE 5432
HEALTHCHECK --interval=10s --timeout=5s --retries=5 CMD pg_isready -U postgres