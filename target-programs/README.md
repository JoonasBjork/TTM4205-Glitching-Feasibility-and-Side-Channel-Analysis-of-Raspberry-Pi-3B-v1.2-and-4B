# Target programs

Throughout the project, we experimented with multiple variations of target programs with many different characterstics. The programs varied w.r.t. the loop/sleep durations (for supporting different target and ChipWhisperer frequencies), the operations done (simple looping vs heavy computations vs IO operations), the number of loops and sleeps, and the number of triggers. The code is short and quite self explanatory. 

## Compilation

Before compiling the C files, you must build WiringPi. After this, you must provide WiringPi as a flag during compilation. For example:

```shell
gcc input-filename.c -o output-filename -lwiringPi
```