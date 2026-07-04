from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.users_request_builder import UsersRequestBuilder 

class Graph:
    def __init__(self, config):
        client_id = config['clientId']
        tenant_id = config['tenantId']
        client_secret = config['clientSecret']

        self.client_credential = ClientSecretCredential(
            tenant_id, client_id, client_secret
        )
        self.app_client = GraphServiceClient(self.client_credential)

    async def get_app_only_token(self):
        graph_scope = 'https://graph.microsoft.com/.default'
        access_token = await self.client_credential.get_token(graph_scope)
        return access_token.token

    async def get_users(self):
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            select=['displayName', 'id', 'mail'],
            top=25,
            orderby=['displayName']
        )
        request_config = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        users = await self.app_client.users.get(request_configuration=request_config)
        return users

    async def make_graph_call(self):
        org = await self.app_client.organization.get()
        return org.value[0]
