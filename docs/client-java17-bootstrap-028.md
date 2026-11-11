# Minecraft 1.20 Java 17 platform synchronization test 028

PPSA99878/01.000.028 uses runtime source 01bd877. PS5 HotSpot
PlatformMutex and PlatformMonitor use early pools of native mutexes
and conditions with checked initialization and release.

The 027 fault report points to a pthread_mutex_lock call during class
metadata allocation. The native mutex initialization result was not
captured. The 028 trace records native pool counts and explicit
initialization refusals. Physical tests reached the original Minecraft Main entry on two retained
runs and then aborted in native code during row 3. Both runs initialized
all 4096 mutex and 4096 condition slots. Neither retained trace shows a
checked synchronization initialization refusal. The abort caller is
unresolved and the title screen was not reached.

The Java 17 target, ordered patch checks, host sanitizer pool checks
and all 21 launcher host checks passed.

The signed package and byte comparison of the update passed.

Signed full ZIP SHA-256
`5d60af958ccaeed32d5420805df7274686a713fea77c76f9f5ad6a98ee8c48ae`.
