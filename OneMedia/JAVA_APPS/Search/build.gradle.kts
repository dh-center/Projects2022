
plugins {
    id("com.github.johnrengelman.shadow") version "5.2.0"
    java
    kotlin("jvm") version "1.5.20"
    kotlin("plugin.serialization") version "1.5.20"
}

group = "ru.onemedia"
version = "1.0-SNAPSHOT"

repositories {
    mavenLocal()
    mavenCentral()
}


sourceSets.main {
    java.srcDirs("src/main/java", "src/main/kotlin")
}


val ktorVersion = "1.6.1"
dependencies {
    implementation(kotlin("stdlib"))
    implementation("org.junit.jupiter:junit-jupiter:5.7.0")
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.6.0")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine")
    // ktor
    implementation("io.ktor:ktor-server-core:$ktorVersion")
    implementation("io.ktor:ktor-server-netty:1.6.1")
    implementation("ch.qos.logback:logback-classic:1.2.3")
    // lucene
    implementation("org.apache.lucene:lucene-core:8.9.0")
    implementation("org.apache.lucene:lucene-analyzers-common:8.9.0")
    implementation("org.apache.lucene:lucene-queryparser:8.9.0")
    // serialization
    implementation("io.ktor:ktor-serialization:$ktorVersion")
    // async database driver
    implementation("com.github.jasync-sql:jasync-postgresql:1.2.2")
    // logging
    implementation("ch.qos.logback:logback-classic:1.2.3")
}



tasks.getByName<Test>("test") {
    useJUnitPlatform()
}

val jar by tasks.getting(Jar::class) {
    manifest {
        attributes["Main-Class"] = "ru.onemedia.ApplicationKt"
    }
}