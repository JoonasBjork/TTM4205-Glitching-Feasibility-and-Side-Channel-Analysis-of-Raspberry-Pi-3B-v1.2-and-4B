#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <unistd.h>

int main(void)
{
    FILE *fp;

    fp = fopen("output.txt", "a");
    if (fp == NULL)
    {
        perror("Error opening file");
        return 1;
    }

    const char *gpio_num = "18";

    wiringPiSetupPinType(WPI_PIN_BCM);

    pinMode(18, OUTPUT);
    digitalWrite(18, LOW);

    volatile long i, j, k, count = 0;

    // Trigger HIGH before operation
    digitalWrite(18, HIGH);
    int iter = 0;

    k = 12345678915678;
    for (i = 0; i < 9; i++)
    {
        digitalWrite(18, LOW);
        fputc('a', fp);
        fflush(fp);
        digitalWrite(18, HIGH);
    }

    // Trigger LOW after operation
    digitalWrite(18, LOW);

    fclose(fp);

    fp = fopen("output.txt", "r");
    if (fp == NULL)
    {
        perror("Error reopening file for reading");
        return 1;
    }

    int c;
    while ((c = fgetc(fp)) != EOF)
    {
        putchar(c);
    }
    fclose(fp);

    remove("output.txt");

    gpio_unexport(gpio_num);

    return 0;
}
