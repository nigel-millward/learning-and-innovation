from snowflake.snowpark import Session


class SnowflakeSession:
    connection_parameters = {
        "account": "bbcstudios_test.eu-west-1",
        "user": "<user_account>",
        "password": "<password>",
        "role": "ACCOUNTADMIN",  # optional
        "warehouse": "SDP_ENGINEERING_WH",  # optional
        "database": "SDP_BRONZE",  # optional
        "schema": "GAM_TEST",  # optional
    }

    def create(self):
        return Session.builder.configs(self.connection_parameters).create()
