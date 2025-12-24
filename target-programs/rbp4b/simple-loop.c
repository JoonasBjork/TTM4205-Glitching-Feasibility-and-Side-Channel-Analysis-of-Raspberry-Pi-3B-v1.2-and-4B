#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <wiringPi.h>

int main(void)
{
    const char *gpio_num = "18";

    wiringPiSetupPinType(WPI_PIN_BCM);

    pinMode(18, OUTPUT);
    digitalWrite(18, LOW);

    volatile int i, j, k, count = 0;
    // Trigger HIGH before operation
    digitalWrite(18, HIGH);
    k = 0;
    for (i = 0; i < 10000; i++)
    {
        for (j = 0; j < 10000; j++)
        {
            k++;
        }
    }

    printf("%d %d %d %d\n", i, j, k, count++);
    // Trigger LOW after operation
    digitalWrite(18, LOW);

    gpio_unexport(gpio_num);

    return 0;
}
