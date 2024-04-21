# apache-flink

### What is apache flink?
Apache Flink is a framework and distributed processing engine for stateful computations over unbounded and bounded data streams. Flink has been designed to run in all common cluster environments, perform computations at in-memory speed and at any scale.
For example, you can also automate data transformation and processing by writing stored procedures and scheduling those procedures as tasks in Snowflake.

apache flink documentation can be found here:
https://flink.apache.org/


### Learning and innovation
As part of learning and innovation day, I developed a data pipeline using apache flink:
- read text from local file system
- count data using a flatmap, output tuplic with word name and count ("dance", "1")
- output to target folder

### Next steps
- parameterize inputs as string[] args in main method, so can pass inputs when running the jar
- Add flink options to parametize inputs within flink
- Use fascade design pattern, to hide implementaton in pipeline - inputs and sink
- explore other sources - sqs, s3, kafka
- explore other sinks - firehose
- setup apache avro or protobuf for schemas/transformations
- Add integration tests to run the pipeline locally
- setup 'aws managed flink' with terraform

