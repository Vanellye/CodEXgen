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
        ndk {
            abiFilters += listOf("armeabi-v7a", "x86")
        }
        externalNativeBuild {
            cmake { cppFlags += "-std=c++11" }
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_7
        targetCompatibility = JavaVersion.VERSION_1_7
    }

    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
            version = "3.22.1"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
}
