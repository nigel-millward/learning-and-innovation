package org.example;

public class Main {
    public static void main(String[] args) {
        System.out.println("Hello world!");

        String sumString = addTwoStrings("4", "5");
        System.out.println(sumString);

        Double sumDouble =  addTwoDoubles(1.0, 2.0);
        System.out.println(sumDouble);
    }

    private static String addTwoStrings(String first, String second){

        int firstInt = Integer.parseInt(first);
        int secondInt = Integer.parseInt(second);
        int sum = firstInt + secondInt;
        return String.valueOf(sum);
    }

    private static Double addTwoDoubles(Double first, Double second){
        return first + second;
    }

    private static BigDecimal addTwoBigDecimals(BigDecimal first, BigDecimal second){
        return first.add(second);
    }
}




