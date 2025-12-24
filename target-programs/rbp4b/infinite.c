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

    while (1)
    {
        // Trigger HIGH before operation
        digitalWrite(18, HIGH);
        int iter = 0;

        while (iter < 1)
        {
            k = 0;
            for (i = 0; i < 500; i++)
            {
                for (j = 0; j < 10000; j++)
                {
                    k++;
                }
            }

            printf("%d %d %d %d\n", i, j, k, count++);
            iter++;
        }

        iter = 0;

        // Trigger LOW after operation
        digitalWrite(18, LOW);
    }

    return 0;
}
