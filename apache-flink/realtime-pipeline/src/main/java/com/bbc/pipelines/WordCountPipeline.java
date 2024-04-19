package com.bbc.pipelines;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.serialization.SimpleStringEncoder;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.MemorySize;
import org.apache.flink.connector.file.sink.FileSink;
import org.apache.flink.connector.file.src.FileSource;
import org.apache.flink.connector.file.src.reader.TextLineInputFormat;
import org.apache.flink.core.fs.Path;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.filesystem.rollingpolicies.DefaultRollingPolicy;
import org.apache.flink.util.Collector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;


public class WordCountPipeline {
    private static final Logger LOG = LoggerFactory.getLogger(WordCountPipeline.class);
    private static final String inputPath = "file:///Users/millwn04/development/learning-and-innovation/apache-flink/realtime-pipeline/src/main/resources/testdata/wordcount/example_data_1.csv";
    private static final String outputPath = "file:///Users/millwn04/development/learning-and-innovation/apache-flink/realtime-pipeline/target/word-count-pipeline";
    private final StreamExecutionEnvironment env;

    public WordCountPipeline() {
        env = StreamExecutionEnvironment.getExecutionEnvironment();
    }

    public void streamData() throws Exception {

        DataStream<String> source = env.fromSource(
                FileSource.forRecordStreamFormat(
                        new TextLineInputFormat(),
                        new Path(inputPath)
                ).build(),
                WatermarkStrategy.noWatermarks(),
                "file-input"
        );

        DataStream<Tuple2<String, Integer>> counts =
                source.flatMap(new LineSplitter())
                        .name("tokenizer")
                        .keyBy(value -> value.f0) // This is similar to a GROUP BY clause in a SQL query.
                        .sum(1)
                        .name("counter");

        counts.sinkTo(FileSink.<Tuple2<String, Integer>>forRowFormat(
                                new Path(outputPath), new SimpleStringEncoder<>())
                        .withRollingPolicy(
                                DefaultRollingPolicy.builder()
                                        .withMaxPartSize(MemorySize.ofMebiBytes(1))
                                        .withRolloverInterval(Duration.ofSeconds(10))
                                        .build())
                        .build())
                .name("file-sink");


        env.execute("WordCount");
    }

    /**
     * The function takes a line (String) and splits it into multiple pairs in the form of "(word,1)
     */
    public class LineSplitter implements FlatMapFunction<String, Tuple2<String, Integer>> {
        @Override
        public void flatMap(String value, Collector<Tuple2<String, Integer>> out) {
            // normalize and split the line
            String[] tokens = value.toLowerCase().split("\\W+");

            // emit the pairs
            for (String token : tokens) {
                if (!token.isEmpty()) {
                    out.collect(new Tuple2<>(token, 1));
                }
            }
        }
    }
}
