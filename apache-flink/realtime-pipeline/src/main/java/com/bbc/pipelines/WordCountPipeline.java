package com.bbc.pipelines;

import com.bbc.transformations.LineSplitter;
import lombok.extern.slf4j.Slf4j;
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


import java.time.Duration;


@Slf4j
public class WordCountPipeline {
    private static final String inputPath = "file:///Users/millwn04/development/learning-and-innovation/apache-flink/realtime-pipeline/src/main/resources/testdata/wordcount/safety_dance.csv";
    private static final String outputPath = "file:///Users/millwn04/development/learning-and-innovation/apache-flink/realtime-pipeline/target/wordcount";

    public void streamData() throws Exception {
        log.info("Pipeline run starting");
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();


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

        /*
        It contains at least 15 minutes worth of data
        It hasn’t received new records for the last 5 minutes
        The file size has reached 1 GB (after writing the last record)
         */
        counts.sinkTo(FileSink
                        .<Tuple2<String, Integer>>forRowFormat(
                                new Path(outputPath), new SimpleStringEncoder<>())
                        .withRollingPolicy(
                                DefaultRollingPolicy.builder()
                                        .withInactivityInterval(Duration.ofMinutes(5))
                                        .withRolloverInterval(Duration.ofMinutes(15))
                                        .withMaxPartSize(MemorySize.ofMebiBytes(1000))
                                        .build())

                        .build())
                .name("file-sink");


        env.execute("WordCount");
    }
}


