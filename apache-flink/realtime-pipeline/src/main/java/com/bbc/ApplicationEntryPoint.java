package com.bbc;

import com.bbc.pipelines.WordCountPipeline;
import lombok.extern.slf4j.Slf4j;


@Slf4j
public class ApplicationEntryPoint {

    public static void main(String[] args)  {

        try {
             new WordCountPipeline().streamData();
        } catch (Exception e){
            log.info("Failed to stream data with the flink application due to an error" + e.getCause());
        }
    }
}