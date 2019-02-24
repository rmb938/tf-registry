from registry.cmd.app import TFRegistryApplication
from registry.cmd.commands.run import RunRegistry


def main():
    app = TFRegistryApplication()
    RunRegistry(app).register(app)
    app.run()


if __name__ == "__main__":
    main()
