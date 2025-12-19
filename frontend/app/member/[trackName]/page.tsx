import React from 'react'

export default async function MemberTrackPage({ params }: { params: Promise<Record<string, string>> }) {
    const { trackName } = await params;
  return (
      <>
          <h1>Member Track { trackName }</h1>
      </>
  )
}
