import { SeeCanRegisterQuery } from '../generated/graphql';
import { serverGraphQL } from '../utils/api_utils';
import { API } from '../utils/api.server';
import { gql } from '@apollo/client';
import type { Metadata } from 'next';
import RegisterForm from './form';
import { print } from "graphql";

const CAN_REGISTER = gql`
  query SeeCanRegister{
    canRegister
  }
`;

export const metadata: Metadata = {
  description: "Register in Team Bdaya Now now Start your free Courses",
  keywords: "Register"
}

export default async function RegisterPage() {
  const [resTracks, canRegister] = await Promise.allSettled(
    [
      API.GET("/tracks/", { next: { revalidate: 300 } }),
      serverGraphQL<SeeCanRegisterQuery>(print(CAN_REGISTER))
    ]
  );

  if (resTracks.status === "fulfilled" && resTracks.value.response.ok && canRegister.status === "fulfilled") {
    return <RegisterForm tracks={resTracks.value.data || []} canRegister={canRegister.value.canRegister || true} />
  }
  return <RegisterForm tracks={[]} canRegister={false} />
}

