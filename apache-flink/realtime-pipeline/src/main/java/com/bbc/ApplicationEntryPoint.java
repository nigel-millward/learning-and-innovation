package com.bbc;

import com.bbc.pipelines.WordCountPipeline;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class ApplicationEntryPoint {

    private static final Logger LOG = LoggerFactory.getLogger(ApplicationEntryPoint.class);

    public static void main(String[] args)  {

        try {
            new WordCountPipeline().streamData();

        } catch (Exception e){
            LOG.error("Failed to stream data with the flink application due to an error" + e.getCause());
        }
    }
}