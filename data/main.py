import asyncio
import os
from graph import Graph
from azure.core.exceptions import ClientAuthenticationError
from azure.identity.aio import ClientSecretCredential

async def main():
    print('Python Graph App-Only Tutorial\n')

    # Read credentials
    client_id = os.getenv("CLIENT_ID")
    tenant_id = os.getenv("TENANT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # Validate credentials BEFORE creating Graph()
    try:
        # Try to get a token to verify credentials
        test_credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

        # Attempt a simple token request
        await test_credential.get_token("https://graph.microsoft.com/.default")

    except ClientAuthenticationError as e:
        print("❌ Invalid credentials. Please check your Tenant ID, Client ID, and Client Secret.")
        print("Error:", e.message)
        return

    except Exception as e:
        print("❌ Unexpected error during authentication.")
        print("Error:", str(e))
        return

    # If we reach here → credentials are valid
    print("✅ Credentials validated successfully.\n")

    config = {
        "clientId": client_id,
        "tenantId": tenant_id,
        "clientSecret": client_secret
    }

    graph = Graph(config)

    choice = -1

    while choice != 0:
        print('Please choose one of the following options:')
        print('0. Exit')
        print('1. Display access token')
        print('2. List users')
        print('3. Make a Graph call')

        try:
            choice = int(input())
        except ValueError:
            choice = -1

        if choice == 0:
            print('Goodbye...')
        elif choice == 1:
            await display_access_token(graph)
        elif choice == 2:
            await list_users(graph)
        elif choice == 3:
            await make_graph_call(graph)
        else:
            print('Invalid choice!\n')

async def display_access_token(graph: Graph):
    token = await graph.get_app_only_token()
    print('App-only token:', token, '\n')

async def list_users(graph: Graph):
    try:
        users_page = await graph.get_users()
    except Exception as e:
        print("❌ Error listing users:", str(e))
        return

    if users_page and users_page.value:
        for user in users_page.value:
            print('User:', user.display_name)
            print('  ID:', user.id)
            print('  Email:', user.mail)

        more_available = users_page.odata_next_link is not None
        print('\nMore users available?', more_available, '\n')

async def make_graph_call(graph: Graph):
    try:
        org = await graph.make_graph_call()
    except Exception as e:
        print("❌ Error making Graph call:", str(e))
        return

    print("Organization:", org.display_name)
    print("Tenant ID:", org.id)

    if org.verified_domains:
        print("Verified Domains:")
        for domain in org.verified_domains:
            print(" -", domain.name)

    if org.verified_domains:
        print("Default Domain:", org.verified_domains[0].name)

    print("Country:", org.country_letter_code)

    if org.technical_notification_mails:
        print("Technical Contact Emails:")
        for email in org.technical_notification_mails:
            print(" -", email)

    print()

asyncio.run(main())
