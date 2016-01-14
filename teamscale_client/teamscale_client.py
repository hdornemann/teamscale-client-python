import requests
import simplejson as json
from requests.auth import HTTPBasicAuth

class TeamscaleClient:
    """Basic Python service client to access Teamscale's REST Api.

    Request handling done with:
    http://docs.python-requests.org/en/latest/

    Args:
        url (str): The url to Teamscale (including the port)
        username (str): The username to use for authentication
        password (str): The password/api key to use for authentication
        project (str): The project on which to work
    """

    def __init__(self, url, username, password, project):
        self.url = url
        self.username = username
        self.auth_header = HTTPBasicAuth(username, password)
        self.project = project

    def put(self, url, json, parameters):
        """Sends a put request to the given service url with the json payload as content.

        Args:
            url (str):  The URL for which to execute a PUT request
            json: The JSON Object to attach as content
            parameters (dict): parameters to attach to the url

        Returns:
            requests.Response: request's response

        Raises:
            Exception: If anything goes wrong
        """
        response = requests.put(url, params=parameters, json=json, headers={'Content-Type':'application/json'}, auth=self.auth_header)
        if response.status_code != 200:
            raise Exception("ERROR: PUT "+url+": {}:{}".format(response.status_code, response.text))
        return response

    def upload_findings(self, findings, timestamp, message, partition):
        """Uploads a list of findings

        Args:
            findings: findings data in json format.
                The findings should have the following format::

                    [
                        {
                            findings: [
                                {
                                    findingTypeId: "<external-finding-type-id>",
                                    message: "<findings message>",
                                    assessment: RED/YELLOW,
                                    startLine: 1,
                                    endLine: 1,
                                    startOffset: 1,
                                    endOffset: 26
                                }
                            ],
                            path: "path/to/file/in/teamscale"
                        },
                        ...
                    ]
            timestamp (int): timestamp (unix format) for which to upload the findings
            message (str): The message to use for the generated upload commit
            partition (str): The partition's id into which the findings should be added

        Returns:
            requests.Response: object generated by the request

        Raises:
            Exception: If anything goes wrong
        """
        return self._upload_external_data("add-external-findings", findings, timestamp, message, partition)

    def upload_metrics(self, metrics, timestamp, message, partition):
        """Uploads a list of metrics

        Args:
            metrics: metrics data in json format.
                The metrics should have the following format::

                    [
                        {
                            "metrics": {
                                "<metric-id-1>": <metric-value>,
                                    "<metric-id-2>": <metric-value>
                            },
                            "path": "path/to/file/in/teamscale"
                        },
                        ...
                    ]
            timestamp (int): timestamp (unix format) for which to upload the metrics
            message (str): The message to use for the generated upload commit
            partition (str): The partition's id into which the metrics should be added

        Returns:
            requests.Response: object generated by the upload request

        Raises:
            Exception: If anything goes wrong
        """
        return self._upload_external_data("add-external-metrics", metrics, timestamp, message, partition)

    def _upload_external_data(self, service_name, json_data, timestamp, message, partition):
        """Uploads externals data in json format

        Args:
            service_name (str): The service name to which to upload the data
            json_data: data in json format
            timestamp (int): timestamp (unix format) for which to upload the data
            message (str): The message to use for the generated upload commit
            partition (str): The partition's id into which the data should be added

        Returns:
            requests.Response: object generated by the request

        Raises:
            Exception: If anything goes wrong
        """
        service_url = self.get_project_service_url(service_name)
        parameters = {
            "t" : timestamp,
            "message" : message,
            "partition" : partition,
            "skip-session" : "true"
        }
        return self.put(service_url, json_data, parameters)



    def get_project_service_url(self, service_name):
        """Returns the full url pointing to a service.

        Args:
           service_name(str): the name of the service for which the url should be generated

        Returns:
            str: The full url
        """
        return "%s/p/%s/%s/" % (self.url, self.project, service_name)

    def read_json_from_file(self, file_path):
        """Reads JSON content from a file and parses it to ensure basic integrity.

        Args:
            file_path (str): File from which to read the JSON content.

        Returns:
            The parsed JSON data."""
        with open(file_path) as json_file:
            json_data = json.load(json_file)
            return json_data

