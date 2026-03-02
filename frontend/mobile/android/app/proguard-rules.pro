-keep class com.openzhixue.** { *; }
-keep class io.flutter.** { *; }
-keep class * extends java.lang.reflect.** { *; }

-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable
-keepattributes RuntimeVisibleAnnotations,RuntimeInvisibleAnnotations

-dontwarn javax.annotation.**
-dontwarn kotlin.Unit
-dontwarn retrofit2.Platform$Java8
