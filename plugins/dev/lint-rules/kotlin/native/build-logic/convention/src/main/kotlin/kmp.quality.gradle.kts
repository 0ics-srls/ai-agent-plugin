// The gate every module shares: every warning of the compiler is an error.

// Every compilation of the code turns a warning into an error. The metadata compilations of shared
// source sets are left out, by the owner's decision: there Kotlin/Native warns that two libraries share
// a unique_name (Compose's and SQLDelight's runtime), a warning of the dependencies that no option
// silences; the same sources are compiled for every target, where the warnings stay errors.
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompilationTask<*>>().configureEach {
    compilerOptions.allWarningsAsErrors.set(!name.endsWith("KotlinMetadata"))
}

// What the app ships — each target's runtime classpath, the iOS klibs — is locked in the module's
// gradle.lockfile, written by `./gradlew resolveAndLockAll --write-locks`: the audit reads it, and a
// version that changes without a new lock fails the build. The classpaths of tests and tools stay out.
val shipped =
    configurations.matching { config ->
        val shipping = config.name.endsWith("untimeClasspath") || config.name.endsWith("CompileKlibraries")
        shipping && !config.name.contains("test", ignoreCase = true)
    }
shipped.configureEach { resolutionStrategy.activateDependencyLocking() }

tasks.register("resolveAndLockAll") {
    notCompatibleWithConfigurationCache("resolves the configurations while it runs")
    doFirst { require(gradle.startParameter.isWriteDependencyLocks) { "run it with --write-locks" } }
    doLast { shipped.filter { it.isCanBeResolved }.forEach { it.incoming.resolutionResult.allComponents } }
}
