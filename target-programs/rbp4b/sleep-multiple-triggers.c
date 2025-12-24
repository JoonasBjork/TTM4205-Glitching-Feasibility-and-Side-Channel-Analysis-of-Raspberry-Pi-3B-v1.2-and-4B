#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <unistd.h>

int main(void)
{
    const char *gpio_num = "18";

    wiringPiSetupPinType(WPI_PIN_BCM);

    pinMode(18, OUTPUT);
    digitalWrite(18, LOW);

    volatile long i, j, k, count = 0;

    // Trigger HIGH before operation
    digitalWrite(18, HIGH);
    int iter = 0;

    k = 12345678915678;
    for (i = 0; i < 250; i++)
    {
        for (j = 0; j < 150; j++)
        {
            k++;
            volatile long a = k / 123456723456;
        }
    }

    digitalWrite(18, LOW);
    digitalWrite(18, HIGH);
    digitalWrite(18, LOW);
    digitalWrite(18, HIGH);
    digitalWrite(18, LOW);

    usleep(50);

    digitalWrite(18, LOW);
    digitalWrite(18, HIGH);
    digitalWrite(18, LOW);
    digitalWrite(18, HIGH);
    digitalWrite(18, LOW);

    k = 12345678915678;
    for (i = 0; i < 250; i++)
    {
        for (j = 0; j < 150; j++)
        {
            k++;
            volatile long a = k / 123456723456;
        }
    }

    digitalWrite(18, LOW);
    digitalWrite(18, HIGH);
    digitalWrite(18, LOW);
    digitalWrite(18, HIGH);
    digitalWrite(18, LOW);

    printf("%d %d %d %d\n", i, j, k, count++);

    // Trigger LOW after operation
    digitalWrite(18, LOW);

    gpio_unexport(gpio_num);

    return 0;
}
