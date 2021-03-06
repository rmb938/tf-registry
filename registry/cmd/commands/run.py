import argparse
import os
from ipaddress import ip_address

import alembic.command
import alembic.config
import boto3
import botocore.exceptions
import cherrypy
from clify.command import Command

from registry.http.app import Application
from registry.http.mounts.root.mount import RootMount
from registry.sql.database import Database


class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, help=None, **kwargs):
        if envvar in os.environ:
            default = os.environ.get(envvar, default)
        if required and default:
            required = False
        if help is not None:
            help += " [Environment Variable: $" + envvar + "]"

        if default is None:
            default = argparse.SUPPRESS

        super(EnvDefault, self).__init__(default=default, required=required, help=help, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):  # pragma: no cover
        setattr(namespace, self.dest, values)


class RunRegistry(Command):

    def __init__(self, application):
        super().__init__('run', 'Run the TF Registry')
        self.leader_elector = None
        self.application = application

    def setup_arguments(self, parser):
        parser.add_argument("--bind-address", action=EnvDefault, envvar="HTTP_ADDRESS", required=False,
                            default="0.0.0.0", help="The IP address to listen on", type=ip_address)
        parser.add_argument("--port", action=EnvDefault, envvar="HTTP_PORT", required=False, default=8080,
                            help="The port for the registry to listen on", type=int)

        # SSL
        parser.add_argument("--cert", action=EnvDefault, envvar="HTTPS_CERT", required=False,
                            type=argparse.FileType('r'), help="The path to the TLS certificate")
        parser.add_argument("--key", action=EnvDefault, envvar="HTTPS_KEY", required=False, type=argparse.FileType('r'),
                            help="The path to the TLS key")

        # Database
        parser.add_argument("--db-url", action=EnvDefault, envvar="DB_URL", required=True,
                            type=str, help="The URL to the database to connect to")
        parser.add_argument("--db-pool-size", action=EnvDefault, envvar="DB_POOL_SIZE", default=5, type=int,
                            help="The amount of connections to make to the database")

        # S3
        parser.add_argument("--s3-endpoint", action=EnvDefault, envvar="AWS_S3_ENDPOINT_URL", type=str, required=False,
                            help="The S3 endpoint")
        parser.add_argument("--s3-access-key-id", action=EnvDefault, envvar="AWS_ACCESS_KEY_ID", type=str,
                            required=False, help="The S3 access key id for S3")
        parser.add_argument("--s3-secret-access-key", action=EnvDefault, envvar="AWS_SECRET_ACCESS_KEY", type=str,
                            required=False, help="The S3 secret access key for S3")
        parser.add_argument("--s3-bucket", action=EnvDefault, envvar="AWS_S3_BUCKET", required=True, type=str,
                            help="The S3 bucket to store and retreive module artifacts")

    def run(self, args) -> int:
        if (hasattr(args, 'cert') is True and hasattr(args, 'key') is False) or \
                (hasattr(args, 'cert') is False and hasattr(args, 'key') is True):
            self.logger.error("Both the cert and key is required to use SSL")
            return 1
        elif hasattr(args, 'cert') is True and hasattr(args, 'key') is True:
            cherrypy.server.ssl_certificate = args.cert.name
            cherrypy.server.ssl_private_key = args.key.name

        s3_parameters = {}
        if hasattr(args, 's3_endpoint'):
            s3_parameters['endpoint_url'] = args.s3_endpoint

        if hasattr(args, 's3_access_key_id'):
            s3_parameters['aws_access_key_id'] = args.s3_access_key_id

        if hasattr(args, 's3_secret_access_key'):
            s3_parameters['aws_secret_access_key'] = args.s3_secret_access_key

        self.logger.info("Connecting to S3")

        s3_client = boto3.resource('s3', **s3_parameters).meta.client

        try:
            s3_client.head_bucket(Bucket=args.s3_bucket)
        except botocore.exceptions.ClientError as e:
            self.logger.error("Error checking if bucket exists: %s", e)
            return 1
        except botocore.exceptions.NoCredentialsError as e:
            self.logger.error("Error loading S3 credentials: %s", e)
            return 1

        self.logger.info("Connecting to database")

        database = Database(db_url=args.db_url, pool_size=args.db_pool_size)
        database.connect()

        self.logger.info("Running SQL migrations")

        config = alembic.config.Config("alembic.ini")
        config.set_main_option("sqlalchemy.url", database.db_url)
        config.attributes['connection'] = database.engine.connect()

        alembic.command.upgrade(config, 'head')

        http_app = Application(logging_config=None, debug=True)
        http_app.register_mount(RootMount(http_app, database, args.s3_bucket, s3_client))
        http_app.setup()

        self.logger.info("Running CherryPy Webserver")

        cherrypy.config.update({
            'global': {
                'environment': 'production',
                'server.socket_host': str(args.bind_address),
                'server.socket_port': args.port,
            }
        })
        cherrypy.engine.start()
        cherrypy.engine.block()

        database.engine.dispose()

        return 0

    def on_shutdown(self, signum=None, frame=None):
        pass
