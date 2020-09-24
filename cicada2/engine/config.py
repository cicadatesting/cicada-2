import os


CONTAINER_NETWORK = os.getenv(
    "CONTAINER_NETWORK", "cicada"
)  # NOTE: possibly default to engine's network
CREATE_NETWORK = os.getenv("CREATE_NETWORK", "true").lower() in ["true", "y", "yes"]
HEALTHCHECK_INITIAL_WAIT = int(os.getenv("HEALTHCHECK_INITIAL_WAIT", "2"))
HEALTHCHECK_MAX_RETRIES = int(os.getenv("HEALTHCHECK_MAX_RETRIES", "5"))
INITIAL_STATE_FILE = os.getenv("INITIAL_STATE_FILE")
POD_NAMESPACE = os.getenv("POD_NAMESPACE", "default")
POD_SERVICE_ACCOUNT = os.getenv("POD_SERVICE_ACCOUNT", "default")
REPORTS_FOLDER = os.getenv("REPORTS_FOLDER", "/reports")
RUN_ID = os.getenv("RUN_ID")
TASK_TYPE = os.getenv("TASK_TYPE", "docker")
TESTS_FOLDER = os.getenv("TESTS_FOLDER", "/tests")
