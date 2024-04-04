'use client';
import {ApolloClient, InMemoryCache, HttpLink, ApolloLink, split} from '@apollo/client';
import {WebSocketLink} from '@apollo/client/link/ws';
import {getMainDefinition} from '@apollo/client/utilities';
import {setContext} from "@apollo/client/link/context"
import {onError} from "@apollo/client/link/error"

const HASURA_URL = process.env.NEXT_PUBLIC_GQL_DOMAIN
const WS_HASURA_URL = process.env.NEXT_PUBLIC_GQL_WS_DOMAIN

console.log(HASURA_URL)
console.log(WS_HASURA_URL)

const getAccessToken = async () => {
    return localStorage.getItem('access');
}

// Enhanced HttpLink to include headers for HTTP connections
const httpLink = new HttpLink({
    uri: HASURA_URL,
    credentials: 'include',
});

const authLink = setContext((_, {headers}) => {
    return {
        headers: {
            ...headers,
            Authorization: `Bearer ${getAccessToken()}`
        },
    }
})


const wsLink = process.browser ? new WebSocketLink({
    uri: WS_HASURA_URL,
    options: {
        reconnect: true,
        connectionParams: async () => {
            const token = await getAccessToken()
            return {
                headers: {
                    // "x-hasura-admin-secret": "gamespw",
                    Authorization: `Bearer ${token}`
                },
            }
        },
    },
}) : null;

const errorLink = onError(({graphQLErrors, networkError, response}) => {
    if (graphQLErrors) {
        // graphQLErrors.map(error => Sentry.captureException(error))

        // workaround for unhandled mutation errors
        // https://github.com/apollographql/apollo-client/issues/5708
        response.errors = undefined
    }
})


const link = split(
    ({query}) => {
        const definition = getMainDefinition(query)
        return (
            definition.kind === "OperationDefinition" &&
            definition.operation === "subscription"
        )
    },
    wsLink,
    authLink.concat(httpLink)
)

const links = ApolloLink.from([errorLink, link])

const client = new ApolloClient({
    link: links,
    cache: new InMemoryCache(),
})

export default client;
