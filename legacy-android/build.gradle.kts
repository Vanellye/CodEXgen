plugins {
    id("com.android.application")
}

android {
    namespace = "com.vanellye.codexgen.legacy"
    compileSdk = 29

    defaultConfig {
        applicationId = "com.vanellye.codexgen.legacy"
        minSdk = 11
        targetSdk = 29
        versionCode = 1
        versionName = "1.0-legacy"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
}
