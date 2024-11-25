# First stage: Build
FROM eclipse-temurin:17-jdk-jammy AS builder

# Set working directory
WORKDIR /app

# Copy Gradle files
COPY gradlew /app/gradlew
COPY gradle /app/gradle
COPY build.gradle /app
COPY settings.gradle /app
COPY src /app/src

COPY *.json .

# Make Gradle wrapper executable
RUN chmod +x gradlew

# Build the application
RUN ./gradlew fatJar

# Second stage: Runtime
FROM eclipse-temurin:17-jdk-jammy

WORKDIR /app

# Copy the specific JAR file
COPY --from=builder /app/build/libs/DeviantCord-4.0.5-beta-all.jar app.jar
COPY --from=builder /app/*.json ./

# Set the command to run the application
ENTRYPOINT ["java", "-jar", "app.jar"]