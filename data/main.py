import asyncio
import os

from graph import Graph
from azure.core.exceptions import ClientAuthenticationError
from azure.identity.aio import ClientSecretCredential


async def main():
    print("Python Graph App-Only Tutorial\n")

    # Read credentials
    client_id = os.getenv("CLIENT_ID")
    tenant_id = os.getenv("TENANT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # Validate env vars exist
    if not client_id or not tenant_id or not client_secret:
        print("❌ Missing environment variables.")
        print("Make sure CLIENT_ID, TENANT_ID, CLIENT_SECRET are set.")
        return

    credential = None

    try:
        # Create credential
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

        # Test authentication (this is correct approach)
        await credential.get_token("https://graph.microsoft.com/.default")

    except ClientAuthenticationError as e:
        print("\n❌ Invalid Azure credentials")

        error_text = str(e)
        print("Details:", error_text)

        if "AADSTS90002" in error_text:
            print("Reason: Tenant ID is invalid")
        elif "AADSTS700016" in error_text:
            print("Reason: Client ID not found")
        elif "AADSTS7000215" in error_text:
            print("Reason: Client Secret invalid")

        return

    except Exception as e:
        print("\n❌ Unexpected authentication error")
        print(type(e).__name__)
        print(str(e))
        return

    finally:
        # IMPORTANT: cleanup async credential
        if credential:
            await credential.close()

    print("\n✅ Credentials validated successfully.\n")

    graph = Graph({
        "clientId": client_id,
        "tenantId": tenant_id,
        "clientSecret": client_secret
    })

    while True:
        print("\nPlease choose one of the following options:")
        print("0. Exit")
        print("1. Display access token")
        print("2. List users")
        print("3. Make a Graph call")

        try:
            choice = int(input("> "))
        except ValueError:
            print("❌ Please enter a number.")
            continue

        try:
            if choice == 0:
                print("Goodbye...")
                break

            elif choice == 1:
                await display_access_token(graph)

            elif choice == 2:
                await list_users(graph)

            elif choice == 3:
                await make_graph_call(graph)

            else:
                print("Invalid choice!")

        except ClientAuthenticationError as e:
            print("\n❌ Graph authentication error:", str(e))

        except Exception as e:
            print("\n❌ Runtime error:")
            print(type(e).__name__)
            print(str(e))


async def display_access_token(graph: Graph):
    token = await graph.get_app_only_token()
    print("\nApp-only token:", token, "\n")


async def list_users(graph: Graph):
    users_page = await graph.get_users()

    if users_page and users_page.value:
        for user in users_page.value:
            print("\nUser:", user.display_name)
            print("ID:", user.id)
            print("Email:", user.mail)

        print("\nMore users:", users_page.odata_next_link is not None)


async def make_graph_call(graph: Graph):
    org = await graph.make_graph_call()

    print("\nOrganization:", org.display_name)
    print("Tenant ID:", org.id)

    if org.verified_domains:
        print("\nVerified Domains:")
        for domain in org.verified_domains:
            print(" -", domain.name)

        print("\nDefault Domain:", org.verified_domains[0].name)

    print("Country:", org.country_letter_code)

    if org.technical_notification_mails:
        print("\nTechnical Contact Emails:")
        for email in org.technical_notification_mails:
            print(" -", email)


if __name__ == "__main__":
    asyncio.run(main())
