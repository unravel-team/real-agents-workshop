FROM postgres:15

EXPOSE 5432

ENV POSTGRES_DB=postgres \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres

CMD ["postgres"]
