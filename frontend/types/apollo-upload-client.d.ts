declare module 'apollo-upload-client' {
  import { ApolloLink } from '@apollo/client';

  export interface CreateUploadLinkOptions {
    uri?: string;
    headers?: Record<string, string>;
    credentials?: RequestCredentials;
    fetch?: typeof fetch;
    // add more options as needed
    [key: string]: any;
  }

  export function createUploadLink(options?: CreateUploadLinkOptions): ApolloLink;

  export default createUploadLink;
}
