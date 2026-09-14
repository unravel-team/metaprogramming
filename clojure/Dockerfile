FROM clojure:temurin-21-tools-deps-bookworm

WORKDIR /app
COPY deps.edn ./
RUN clojure -Srepro -P -M:run

COPY src ./src
COPY app ./app
EXPOSE 8080
CMD ["clojure", "-Srepro", "-M:run"]
