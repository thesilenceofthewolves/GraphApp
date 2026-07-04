import asyncio
import configparser

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import CredentialUnavailableError
from msgraph.generated.models.o_data_errors.o_data_error import ODataError

from graph import Graph


async def main():
    print("Python Graph App-Only Tutorial\n")

    # Load settings
    config = configparser.ConfigParser()

    files = config.read(["config.cfg", "config.dev.cfg"])

    if not files:
        print("Error: No configuration file found.")
        return

    if "azure" not in config:
        print("Error: Missing [azure] section in configuration file.")
        return

    azure_settings = config["azure"]

    # Check required settings
    required = ["clientId", "tenantId", "clientSecret"]

    for key in required:
        if key not in azure_settings or not azure_settings[key].strip():
            print(f"Error: Missing '{key}' in the [azure] section.")
            return

    graph = Graph(azure_settings)

    choice = -1

    while choice != 0:
        print("Please choose one of the following options:")
        print("0. Exit")
        print("1. Display access token")
        print("2. List users")
        print("3. Make a Graph call")

        try:
            choice = int(input())
        except ValueError:
            print("Please enter a number.\n")
            continue

        try:
            if choice == 0:
                print("Goodbye...")

            elif choice == 1:
                await display_access_token(graph)

            elif choice == 2:
                await list_users(graph)

            elif choice == 3:
                await make_graph_call(graph)

            else:
                print("Invalid choice!\n")

        except ClientAuthenticationError as e:
            print("\nAuthentication failed.")
            print("Please check your:")
            print(" - Tenant ID")
            print(" - Client ID")
            print(" - Client Secret")
            print()
            print(e)

        except CredentialUnavailableError as e:
            print("\nCredential unavailable:")
            print(e)

        except ODataError as e:
            print("\nMicrosoft Graph returned an error:")

            if e.error:
                print(f"Code: {e.error.code}")
                print(f"Message: {e.error.message}")
            else:
                print(e)

        except Exception as e:
            print("\nUnexpected error:")
            print(type(e).__name__)
            print(e)


async def display_access_token(graph: Graph):
    token = await graph.get_app_only_token()
    print("\nApp-only token:")
    print(token)
    print()


async def list_users(graph: Graph):
    users_page = await graph.get_users()

    if users_page and users_page.value:
        for user in users_page.value:
            print("User:", user.display_name)
            print("  ID:", user.id)
            print("  Email:", user.mail)

        more_available = users_page.odata_next_link is not None
        print("\nMore users available?", more_available)

    print()


async def make_graph_call(graph: Graph):
    org = await graph.make_graph_call()

    print("Organization:", org.display_name)
    print("Tenant ID:", org.id)

    if org.verified_domains:
        print("Verified Domains:")
        for domain in org.verified_domains:
            print(" -", domain.name)

        print("Default Domain:", org.verified_domains[0].name)

    print("Country:", org.country_letter_code)

    if org.technical_notification_mails:
        print("Technical Contact Emails:")
        for email in org.technical_notification_mails:
            print(" -", email)

    print()


if __name__ == "__main__":
    asyncio.run(main())
