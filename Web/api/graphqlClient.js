import {ApolloClient, InMemoryCache, HttpLink, split} from '@apollo/client';
import {WebSocketLink} from '@apollo/client/link/ws';
import {getMainDefinition} from '@apollo/client/utilities';

const HASURA_URL = "http://localhost:8080/v1/graphql";
const WS_HASURA_URL = "ws://localhost:8080/v1/graphql";

// Enhanced HttpLink to include headers for HTTP connections
const httpLink = new HttpLink({
    uri: HASURA_URL,
    credentials: 'include',
    headers: {
        // Directly setting headers here. This assumes you're not doing SSR or you handle the token differently for SSR.
        Authorization: typeof window !== 'undefined' ? `Bearer ${localStorage.getItem('access')}` : '',
    }
});

const wsLink = process.browser ? new WebSocketLink({
    uri: WS_HASURA_URL,
    options: {
        reconnect: true,
        connectionParams: {
            // Assuming the token is available on the client-side. This won't run on the server.
            headers: {
                Authorization: `Bearer ${localStorage.getItem('access')}`,
            },
        },
    },
}) : null;

const link = process.browser ? split(
    ({query}) => {
        const definition = getMainDefinition(query);
        return (
            definition.kind === 'OperationDefinition' &&
            definition.operation === 'subscription'
        );
    },
    wsLink,
    httpLink,
) : httpLink;

const apolloClient = new ApolloClient({
    link,
    cache: new InMemoryCache(),
});

export default apolloClient;
