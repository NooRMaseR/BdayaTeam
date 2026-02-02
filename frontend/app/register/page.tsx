import type { SeeCanRegisterQuery } from '../generated/graphql';
import { CAN_REGISTER } from '../utils/graphql_helpers';
import { serverGraphQL } from '../utils/api_utils';
import { API } from '../utils/api.server';
import type { Metadata } from 'next';
import RegisterForm from './form';

export const metadata: Metadata = {
  description: "Register in Team Bdaya Now now Start your free Courses",
  keywords: "Register"
}

export default async function RegisterPage() {
  const [resTracks, canRegister] = await Promise.all(
    [
      API.GET("/api/tracks/", { next: { revalidate: 300 } }),
      serverGraphQL<SeeCanRegisterQuery>(CAN_REGISTER)
    ]
  );

  if (resTracks.response.ok) {
    return <RegisterForm tracks={resTracks.data || []} canRegister={canRegister.data.canRegister} />
  }
  return <RegisterForm tracks={[]} canRegister={false} />
}

