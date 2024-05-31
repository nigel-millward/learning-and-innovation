package com.bbc.transformations;

import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.util.Collector;

/**
 * The function takes a line (String) and splits it into multiple pairs in the form of "(word,1)
 */
public class LineSplitter implements FlatMapFunction<String, Tuple2<String, Integer>> {
    @Override
    public void flatMap(String in, Collector<Tuple2<String, Integer>> out) {
        // normalize and split the line
        String[] words = in.toLowerCase().split("\\W+");

        // emit the pairs
        for (String word : words) {
            if (word.length() > 0) {
                out.collect(new Tuple2<>(word, 1));
            }
        }
    }
}