#!/usr/bin/env python
from dataclasses import dataclass
from enum import Enum
import hashlib
from queue import Queue
from typing import Literal
from urllib.error import URLError
from urllib import request, parse
import time
import json
import glob
from os import getenv, path
import logging

logger = logging.getLogger("keycloak.provisioning")
logging.basicConfig(
    encoding="utf-8",
    level=f"{getenv('LOG_LEVEL', 'INFO')}",
    format="%(asctime)s %(name)s %(levelname)-6s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

SECRETS_PATH = "/var/run/secrets/keycloak"
CM_PATH = "/opt/keycloak"
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
            logger.info("remote %s updated", self.type)
        self._entities = entities

    @property
    def entities(self) -> list[dict]:
        if self._entities == []:
            logger.warning("remote %s not fetched, though queried", self.type)
        return self._entities

    @property
    def url(self) -> str:
        return self._url


class Remotes(Enum):
    REALMS = RemoteResource("realm")
    CLIENTS = RemoteResource("client")

    @classmethod
    def select_by_type(cls, resource_type: ResourceType):
        match resource_type:
            case "client":
                return cls.CLIENTS
            case "realm":
                return cls.REALMS


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
            if resource_definition["id"] in [
                x["id"] for x in Remotes.REALMS.value.entities
            ]:
                logger.debug(
                    "realm %s (%s) exists in remote definitions: %s",
                    resource_definition["realm"],
                    resource_definition["id"],
                    Remotes.REALMS.value.entities,
                )
                return resource_definition["id"]
        case "client":
            for e in Remotes.CLIENTS.value.entities:
                if e["clientId"] == resource_definition["clientId"]:
                    logger.debug(
                        "client %s (%s) exists in remote definitions: %s",
                        e["clientId"],
                        e["id"],
                        Remotes.CLIENTS.value.entities,
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


class Scheduler:
    folder = CM_PATH
    files: dict
    changes: Queue[str]
    _token: str

    @staticmethod
    def _compute_file_hash(path: str) -> str:
        with open(path, "rb", buffering=0) as f:
            return hashlib.file_digest(f, "sha256").hexdigest()

    def __init__(self):
        self.changes = Queue()
        logger.info(
            "Scheduler watching for resources found in %s for realm %s",
            self.folder,
            REALM,
        )
        files = glob.glob(f"{self.folder}/*.json")
        self.files = {}
        for f in files:
            self.files[f] = self._compute_file_hash(f)
            self.changes.put(f)
        self._apply_changes()
        logger.debug("stored hashes: %s", self.files)

    def _refresh_remote(self):
        """
        Fetch remote states of all handled resource types
        """
        for remote in Remotes:
            logger.debug("Refreshing %s remote definitions", remote)
            resp = request.urlopen(
                request.Request(
                    remote.value.url,
                    method="GET",
                    headers={
                        "Authorization": f"Bearer {self._token}",
                    },
                )
            )
            remote.value.set_entities(json.loads(resp.read()))

    def _apply_changes(self):
        """
        Unpile staged change from self.changes queue
        """
        self._token = generate_token()
        self._refresh_remote()
        while self.changes.empty() == False:
            change = self.changes.get()
            definition_file = path.basename(change)
            create_or_update(
                token=self._token,
                resource_path=change,
                remote=Remotes.select_by_type(definition_file.split("-")[0]).value,
            )
            self.changes.task_done()

    def watch(self):
        """
        Infinite loop looking for changes in the watch folder
        """
        while True:
            files = glob.glob(f"{self.folder}/*.json")
            logger.debug("Found the following files in the watch folder: %s", files)
            for file in files:
                h = self._compute_file_hash(file)
                if file not in self.files.keys() or self.files[file] != h:
                    logger.info("Changes detected on %s", file)
                    self.changes.put(file)
                self.files[file] = h
            if self.changes.empty() == False:
                self._apply_changes()
            time.sleep(15)


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
        time.sleep(10)
        n += 1
    raise TimeoutError("Keycloak REST Api unavailable")


if __name__ == "__main__":
    wait_for_keycloak_ready()
    scheduler = Scheduler()
    scheduler.watch()
