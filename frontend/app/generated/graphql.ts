export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
  DateTime: { input: any; output: any; }
};

/** An enumeration. */
export enum MemberMemberStatusChoices {
  /** Fired */
  Fired = 'FIRED',
  /** Normal */
  Normal = 'NORMAL',
  /** Warning */
  Warning = 'WARNING'
}

export type MemberType = {
  __typename?: 'MemberType';
  bonus: Scalars['Int']['output'];
  code: Scalars['String']['output'];
  collageCode: Scalars['String']['output'];
  email: Scalars['String']['output'];
  joinedAt: Scalars['DateTime']['output'];
  name: Scalars['String']['output'];
  phoneNumber: Scalars['String']['output'];
  status: MemberMemberStatusChoices;
  track: TrackType;
};

export type Query = {
  __typename?: 'Query';
  allSettings?: Maybe<SettingsType>;
  canRegister?: Maybe<Scalars['Boolean']['output']>;
  member?: Maybe<MemberType>;
  track?: Maybe<TrackType>;
};


export type QueryMemberArgs = {
  code?: InputMaybe<Scalars['String']['input']>;
  email?: InputMaybe<Scalars['String']['input']>;
};


export type QueryTrackArgs = {
  track?: InputMaybe<Scalars['String']['input']>;
};

export type SettingsType = {
  __typename?: 'SettingsType';
  heroImage?: Maybe<Scalars['String']['output']>;
  id: Scalars['ID']['output'];
  isRegisterEnabled: Scalars['Boolean']['output'];
  organizerCanEdit: Array<Scalars['String']['output']>;
  siteImage?: Maybe<Scalars['String']['output']>;
};

export type TrackType = {
  __typename?: 'TrackType';
  description?: Maybe<Scalars['String']['output']>;
  id: Scalars['ID']['output'];
  image?: Maybe<Scalars['String']['output']>;
  members: Array<MemberType>;
  prefix: Scalars['String']['output'];
  track: Scalars['String']['output'];
};

export type SettingsSiteImageQueryVariables = Exact<{ [key: string]: never; }>;


export type SettingsSiteImageQuery = { __typename?: 'Query', allSettings?: { __typename?: 'SettingsType', siteImage?: string | null } | null };

export type SettingsHeroImageQueryVariables = Exact<{ [key: string]: never; }>;


export type SettingsHeroImageQuery = { __typename?: 'Query', allSettings?: { __typename?: 'SettingsType', heroImage?: string | null } | null };

export type SettingsImagesQueryVariables = Exact<{ [key: string]: never; }>;


export type SettingsImagesQuery = { __typename?: 'Query', allSettings?: { __typename?: 'SettingsType', siteImage?: string | null, heroImage?: string | null } | null };

export type SeeOrganizerCanEditQueryVariables = Exact<{ [key: string]: never; }>;


export type SeeOrganizerCanEditQuery = { __typename?: 'Query', allSettings?: { __typename?: 'SettingsType', organizerCanEdit: Array<string> } | null };

export type GetAllSettingsQueryVariables = Exact<{ [key: string]: never; }>;


export type GetAllSettingsQuery = { __typename?: 'Query', allSettings?: { __typename?: 'SettingsType', siteImage?: string | null, heroImage?: string | null, isRegisterEnabled: boolean, organizerCanEdit: Array<string> } | null };

export type SeeCanRegisterQueryVariables = Exact<{ [key: string]: never; }>;


export type SeeCanRegisterQuery = { __typename?: 'Query', canRegister?: boolean | null };

export type Get_Track_ImageQueryVariables = Exact<{
  track?: InputMaybe<Scalars['String']['input']>;
}>;


export type Get_Track_ImageQuery = { __typename?: 'Query', track?: { __typename?: 'TrackType', image?: string | null } | null };

export type Get_Member_CodeQueryVariables = Exact<{ [key: string]: never; }>;


export type Get_Member_CodeQuery = { __typename?: 'Query', member?: { __typename?: 'MemberType', code: string } | null };
