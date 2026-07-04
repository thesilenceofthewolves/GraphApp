import asyncio
import configparser

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import CredentialUnavailableError
from msgraph.generated.models.o_data_errors.o_data_error import ODataError

from graph import Graph


async def main():
    print("Python Graph App-Only Tutorial\n")

    # Load configuration
    config = configparser.ConfigParser()

    if not config.read(["config.cfg", "config.dev.cfg"]):
        print("Error: No configuration file found.")
        return

    if "azure" not in config:
        print("Error: Missing [azure] section in configuration.")
        return

    azure_settings = config["azure"]

    # Check required settings
    required = ["clientId", "tenantId", "clientSecret"]

    for key in required:
        if not azure_settings.get(key):
            print(f"Error: Missing '{key}' in the [azure] section.")
            return

    graph = Graph(azure_settings)

    while True:
        print("\nPlease choose one of the following options:")
        print("0. Exit")
        print("1. Display access token")
        print("2. List users")
        print("3. Make a Graph call")

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
        print("Invalid choice!")

except ODataError as e:
    print("\n=== Microsoft Graph Error ===")
    if e.error:
        print(f"Code    : {e.error.code}")
        print(f"Message : {e.error.message}")
    else:
        print(e)

except Exception as e:
    print("\n=== Authentication / Azure Error ===")
    print(f"Exception Type : {type(e).__name__}")
    print(f"Message        : {e}")

    error = str(e)

    if "AADSTS90002" in error:
        print("\nReason: The Tenant ID is invalid or the tenant does not exist.")

    elif "AADSTS700016" in error:
        print("\nReason: The Client ID (Application ID) is invalid or the application was not found.")

    elif "AADSTS7000215" in error:
        print("\nReason: The Client Secret is invalid.")

    elif "AADSTS7000222" in error:
        print("\nReason: The Client Secret has expired.")

    elif "AADSTS500011" in error:
        print("\nReason: Microsoft Graph is not configured for this application.")

    else:
        print("\nNo specific Azure error code was found.")


async def display_access_token(graph: Graph):
    token = await graph.get_app_only_token()
    print("\nAccess Token:\n")
    print(token)


async def list_users(graph: Graph):
    users_page = await graph.get_users()

    if users_page and users_page.value:
        for user in users_page.value:
            print()
            print("User :", user.display_name)
            print("ID   :", user.id)
            print("Email:", user.mail)

        print("\nMore users:", users_page.odata_next_link is not None)


async def make_graph_call(graph: Graph):
    org = await graph.make_graph_call()

    print("\nOrganization:", org.display_name)
    print("Tenant ID   :", org.id)
    print("Country     :", org.country_letter_code)

    if org.verified_domains:
        print("\nVerified Domains:")
        for domain in org.verified_domains:
            print(" -", domain.name)

    if org.technical_notification_mails:
        print("\nTechnical Contact Emails:")
        for email in org.technical_notification_mails:
            print(" -", email)


if __name__ == "__main__":
    asyncio.run(main())
