package org.example.examples;

import java.util.Scanner;

public class NumberReverser {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter an integer: ");

        int number = scanner.nextInt();
        int reversedNumber = reverseNumber(number);
        System.out.println("Reversed number: " + reversedNumber);
    }

    private static int reverseNumber(int n) {
        int reversed = 0;
        while (n != 0) {
            int digit = n % 10; // Extract the last digit of the number
            reversed = reversed * 10 + digit; // Append the digit to the reversed number
            n /= 10; // Remove the last digit from the number
        }
        return reversed;
    }
}
