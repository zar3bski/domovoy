#!/usr/bin/env python
from dataclasses import dataclass
from enum import Enum
from typing import Literal
from urllib.error import URLError
from urllib import request, parse
import time
import json
import glob
from os import getenv, path
import logging

logger = logging.getLogger("keycloak.provisioning")
logging.basicConfig(encoding="utf-8", level=f"{getenv('LOG_LEVEL', 'INFO')}")

SECRETS_PATH = "/var/run/secrets/keycloak"
ROOT_API = "http://localhost:8080"
REALM = getenv("REALM")
type ResourceType = Literal["realm", "client"]


class RemoteResource[ResourceType]:
    """
    Store remote entities for the given ResourceType together with
    its access url
    """

    type: ResourceType
    _url: str
    _entities: list[dict]

    def __init__(self, type: ResourceType):
        self.type = type
        self._entities = []
        match type:
            case "realm":
                self._url = f"{ROOT_API}/admin/realms"
            case "client":
                self._url = f"{ROOT_API}/admin/realms/{REALM}/clients"

    def set_entities(self, entities: list[dict]):
        if self._entities != []:
            logger.warning("remote %s already fetched, unecessary API call", self.type)
        self._entities = entities

    @property
    def entities(self) -> list[dict]:
        if self._entities == []:
            logger.warning("remote %s not fetched, though queried", self.type)
        return self._entities

    @property
    def url(self) -> str:
        return self._url


REMOTE_REALMS = RemoteResource("realm")
REMOTE_CLIENTS = RemoteResource("client")


@dataclass
class ApiCallsParams:
    url: str
    method: Literal["POST", "PUT"]
    action: Literal["create", "update"]
    expected_status_code: int


###############################################


def generate_token() -> str:
    with open(f"{SECRETS_PATH}/BOOTSTRAP_ADMIN_PASSWORD") as admin_password_file:
        with open(f"{SECRETS_PATH}/BOOTSTRAP_ADMIN_USERNAME") as admin_name_file:
            data = parse.urlencode(
                {
                    "username": admin_name_file.read(),
                    "password": admin_password_file.read(),
                    "grant_type": "password",
                    "client_id": "admin-cli",
                }
            )
    req = request.Request(
        f"{ROOT_API}/realms/master/protocol/openid-connect/token", method="POST"
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    resp = request.urlopen(req, data=data.encode())
    if resp.status != 200:
        raise URLError(
            "Unauthorized call to /openid-connect/token with the current credentials"
        )
    else:
        json_data = json.loads(resp.read())
        logger.info("Token generated")
        logger.debug("token payload: %s", json_data)
        return json_data["access_token"]


def get_uuid_if_exists(
    resource_type: ResourceType, resource_definition: dict
) -> str | None:
    """
    Compare remote state with the current <resource_definition>. Identity criterion
    is determined based on <resource_type>
    """
    match resource_type:
        case "realm":
            if resource_definition["id"] in [x["id"] for x in REMOTE_REALMS.entities]:
                logger.debug(
                    "realm %s (%s) exists in remote definitions: %s",
                    resource_definition["realm"],
                    resource_definition["id"],
                    REMOTE_REALMS.entities,
                )
                return resource_definition["id"]
        case "client":
            for e in REMOTE_CLIENTS.entities:
                if e["clientId"] == resource_definition["clientId"]:
                    logger.debug(
                        "client %s (%s) exists in remote definitions: %s",
                        e["clientId"],
                        e["id"],
                        REMOTE_CLIENTS.entities,
                    )
                    return e["id"]


def create_or_update(token: str, resource_path: str, remote: RemoteResource):
    """
    POST OR PUT resource depending on its remote existence
    """
    with open(resource_path) as payload:
        payload_data = payload.read()
        resource_def = json.loads(payload_data)

        resource_uuid = get_uuid_if_exists(
            resource_type=remote.type,
            resource_definition=resource_def,
        )
        if resource_uuid != None:
            params = ApiCallsParams(
                url=f"{remote.url}/{REALM if remote.type == 'realm' else resource_uuid}",
                method="PUT",
                action="update",
                expected_status_code=204,
            )
        else:
            params = ApiCallsParams(
                url=f"{remote.url}",
                method="POST",
                action="create",
                expected_status_code=201,
            )
        logger.info(
            "%s defined in %s: %s",
            remote.type,
            resource_path,
            params.action,
        )
        logger.debug("calling url: %s", params.url)
        req = request.Request(
            url=params.url,
            method=params.method,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        resp = request.urlopen(req, data=payload_data.encode())
        if resp.status == params.expected_status_code:
            logger.info(
                "%s defined in %s successfully %sd",
                remote.type,
                resource_path,
                params.action,
            )
        else:
            logger.warning(
                "%s defined in %s. Failed to %s resource. status code: %s",
                remote.type,
                resource_path,
                params.action,
                resp.status,
            )


def provision(token: str):
    """
    Loop through the .json found in the folder of the current script
    and, identify the existing remote resources and calls create_or_update
    """
    folder = path.dirname(path.realpath(__file__))
    logger.info("Provisioning resources found in %s for realm %s", folder, REALM)
    resources = glob.glob(f"{folder}/*.json")
    logger.info("Realm provisioning")
    resp = request.urlopen(
        request.Request(
            REMOTE_REALMS.url,
            method="GET",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
    )
    REMOTE_REALMS.set_entities(json.loads(resp.read()))
    for resource in [x for x in resources if path.basename(x).startswith("realm-")]:
        create_or_update(token=token, resource_path=resource, remote=REMOTE_REALMS)

    logger.info("Client provisioning")
    resp = request.urlopen(
        request.Request(
            REMOTE_CLIENTS.url,
            method="GET",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
    )
    REMOTE_CLIENTS.set_entities(json.loads(resp.read()))
    for resource in [x for x in resources if path.basename(x).startswith("client-")]:
        create_or_update(token=token, resource_path=resource, remote=REMOTE_CLIENTS)


def wait_doing_nothing():
    logger.info("Wait for the end of times")
    x = False
    while not x:
        time.sleep(100)


def wait_for_keycloak_ready():
    logger.info("Waiting for Keycloak availability")
    n = 0
    while n < 100:
        try:
            request.urlopen(f"{ROOT_API}")
            logger.info("Keycloak ready to accept connections")
            return
        except URLError:
            logger.debug("Waiting for keycloak to accept connections. Attempt n° %s", n)
        time.sleep(5)
        n += 1
    raise TimeoutError("Keycloak REST Api unavailable")


if __name__ == "__main__":
    wait_for_keycloak_ready()
    token = generate_token()
    provision(token)
    wait_doing_nothing()
